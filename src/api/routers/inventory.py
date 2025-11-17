from fastapi import APIRouter, HTTPException, status
import logging

from ..db import fetchall_sql, execute_sql, get_connection, safe_close_connection
from ..models.inventory import Inventory
from .. import queries

router = APIRouter()

def check_inventory_usage(inventory_id: int) -> dict:
    """Kiểm tra xem inventory có đang được sử dụng trong stores không"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(queries.CHECK_INVENTORY_IN_STORES, (inventory_id,))
            stores_count = cursor.fetchone()['count']
            
            return {
                'has_stores': stores_count > 0,
                'stores_count': stores_count,
                'can_delete': stores_count == 0
            }
    finally:
        safe_close_connection(conn)

@router.get("/inventories")
def get_inventory():
    try:
        return fetchall_sql(queries.SELECT_INVENTORIES)
    except Exception as e:
        logging.error(f"Error in get_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/inventories", status_code=status.HTTP_201_CREATED)
def create_inventory(payload: dict):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Tạo inventory record
            inventory_id = payload.get("inventoryID")
            cursor.execute(queries.INSERT_INVENTORY, (
                inventory_id,
                payload.get("warehouse"),
                payload.get("maxStockLevel"),
                payload.get("stockQuantity"),
                payload.get("unitCost"),
                payload.get("inventoryNote"),
                payload.get("inventoryStatus")
            ))
            
            # Nếu có productID, tạo relationship trong tbl_stores
            product_id = payload.get("productID")
            if product_id:
                # Kiểm tra product có tồn tại không
                cursor.execute(queries.SELECT_PRODUCT_BY_ID_FOR_INVENTORY, (product_id,))
                if not cursor.fetchone():
                    raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
                
                # Tạo stores relationship
                cursor.execute(queries.INSERT_STORE_FOR_INVENTORY, (
                    product_id,
                    inventory_id,
                    payload.get("stockQuantity", 0)
                ))
            
            conn.commit()
        return {"message": "Inventory record created", "inventoryID": inventory_id}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in create_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)

@router.put("/inventories/{id}")
def update_inventory(id: int, payload: Inventory):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Cập nhật inventory record
            cursor.execute(queries.UPDATE_INVENTORY, (
                payload.warehouse,
                payload.maxStockLevel,
                payload.stockQuantity,
                payload.unitCost,
                payload.inventoryNote,
                payload.inventoryStatus,
                id
            ))
            
            # Nếu có productID, cập nhật hoặc tạo stores relationship
            if payload.productID:
                # Kiểm tra product có tồn tại không
                cursor.execute(queries.SELECT_PRODUCT_BY_ID_FOR_INVENTORY, (payload.productID,))
                if not cursor.fetchone():
                    raise HTTPException(status_code=404, detail=f"Product with ID {payload.productID} not found")
                
                # Kiểm tra xem stores relationship đã tồn tại chưa
                cursor.execute(queries.SELECT_STORE_FOR_INVENTORY_UPDATE, (id, payload.productID))
                existing_store = cursor.fetchone()
                
                if existing_store:
                    # Cập nhật stores relationship
                    cursor.execute(queries.UPDATE_STORE_FOR_INVENTORY_UPDATE, (payload.stockQuantity, id, payload.productID))
                else:
                    # Tạo stores relationship mới
                    cursor.execute(queries.INSERT_STORE_FOR_INVENTORY_UPDATE, (payload.productID, id, payload.stockQuantity))
            
            conn.commit()
        return {"message": "Inventory updated successfully"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in update_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)

@router.delete("/inventories/{id}")
def delete_inventory(id: int):
    try:
        # Kiểm tra xem inventory có đang được sử dụng không
        usage = check_inventory_usage(id)
        
        if not usage['can_delete']:
            raise HTTPException(
                status_code=400, 
                detail=f"Không thể xóa kho này vì đang được sử dụng trong {usage['stores_count']} bản ghi lưu trữ sản phẩm"
            )
        
        execute_sql(queries.DELETE_INVENTORY, (id,))
        return {"message": "Inventory record deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in delete_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))