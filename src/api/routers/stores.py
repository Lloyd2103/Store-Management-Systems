import datetime
from fastapi import APIRouter, HTTPException, status
import logging

from ..db import fetchall_sql, execute_sql, get_connection, safe_close_connection
from ..models.store import Store
from .. import queries

router = APIRouter()

@router.get("/stores")
def get_store():
    try:
        return fetchall_sql(queries.SELECT_STORES)
    except Exception as e:
        logging.error(f"Error in get_store: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stores/product/{product_id}")
def get_stores_by_product(product_id: int):
    """Lấy tất cả stores của một product"""
    try:
        return fetchall_sql(queries.SELECT_STORES_BY_PRODUCT, (product_id,))
    except Exception as e:
        logging.error(f"Error in get_stores_by_product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stores/inventory/{inventory_id}")
def get_stores_by_inventory(inventory_id: int):
    """Lấy tất cả stores của một inventory"""
    try:
        return fetchall_sql(queries.SELECT_STORES_BY_INVENTORY, (inventory_id,))
    except Exception as e:
        logging.error(f"Error in get_stores_by_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stores", status_code=status.HTTP_201_CREATED)
def create_store(payload: Store):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Kiểm tra product và inventory có tồn tại không
            cursor.execute(queries.SELECT_PRODUCT_FOR_STORE, (payload.productID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Product with ID {payload.productID} not found")
            
            cursor.execute(queries.SELECT_INVENTORY_FOR_STORE, (payload.inventoryID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Inventory with ID {payload.inventoryID} not found")
            
            # Tạo stores relationship
            cursor.execute(queries.INSERT_STORE, (
                payload.productID, 
                payload.inventoryID, 
                payload.storeDate or datetime.datetime.now(), 
                payload.quantityStore, 
                payload.roleStore or 'Manual'
            ))
            
            # Cập nhật stock quantity trong inventory nếu roleStore là Import
            if payload.roleStore == 'Import':
                cursor.execute(queries.UPDATE_INVENTORY_FOR_STORE_IMPORT, (payload.quantityStore, payload.inventoryID))
            
            conn.commit()
            store_id = cursor.lastrowid
        return {"message": "Store created", "storeID": store_id}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in create_store: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)

@router.put("/stores/{id}")
def update_store(id: int, payload: Store):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Kiểm tra product và inventory có tồn tại không
            cursor.execute(queries.SELECT_PRODUCT_FOR_STORE, (payload.productID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Product with ID {payload.productID} not found")
            
            cursor.execute(queries.SELECT_INVENTORY_FOR_STORE, (payload.inventoryID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Inventory with ID {payload.inventoryID} not found")
            
            # Lấy số lượng cũ để tính toán chênh lệch
            cursor.execute(queries.SELECT_STORE_BY_ID, (id,))
            old_store = cursor.fetchone()
            if not old_store:
                raise HTTPException(status_code=404, detail="Store not found")
            
            old_quantity = old_store['quantityStore']
            quantity_diff = payload.quantityStore - old_quantity
            
            # Cập nhật stores relationship
            cursor.execute(queries.UPDATE_STORE, (
                payload.productID, 
                payload.inventoryID, 
                payload.storeDate or datetime.datetime.now(), 
                payload.quantityStore, 
                payload.roleStore or 'Manual', 
                id
            ))
            
            # Cập nhật stock quantity trong inventory nếu có thay đổi
            if quantity_diff != 0 and payload.roleStore in ['Import', 'Manual']:
                cursor.execute(queries.UPDATE_INVENTORY_FOR_STORE_UPDATE, (quantity_diff, payload.inventoryID))
            
            conn.commit()
        return {"message": "Store updated successfully"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in update_store: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)
    
@router.delete("/stores/{id}")
def delete_store(id: int):
    try:
        execute_sql(queries.DELETE_STORE, (id,))
        return {"message": "Store deleted"}
    except Exception as e:
        logging.error(f"Error in delete_store: {e}")
        raise HTTPException(status_code=500, detail=str(e))