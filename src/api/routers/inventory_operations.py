import datetime
from fastapi import APIRouter, HTTPException, status
import logging

from ..db import fetchall_sql, execute_sql, get_connection, safe_close_connection
from ..models.inventory import InventoryImport, InventoryExport, Stocktaking
from .. import queries

router = APIRouter()

@router.post("/inventory/import", status_code=status.HTTP_201_CREATED)
def import_inventory(payload: InventoryImport):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Thêm vào stores (lịch sử nhập kho)
            cursor.execute(queries.INSERT_STORE_FOR_INVENTORY_IMPORT, (payload.productID, payload.inventoryID, payload.importDate or datetime.datetime.now(), payload.quantity))
            
            # Kiểm tra xem inventory record đã tồn tại chưa
            cursor.execute(queries.SELECT_INVENTORY_BY_ID, (payload.inventoryID,))
            inv_exists = cursor.fetchone()
            
            if inv_exists:
                # Cập nhật stock quantity nếu inventory đã tồn tại
                cursor.execute(queries.UPDATE_INVENTORY_FOR_IMPORT, (payload.quantity, payload.unitCost, payload.inventoryID))
            else:
                # Tạo inventory record mới nếu chưa có
                cursor.execute(queries.INSERT_INVENTORY_FOR_IMPORT, (payload.inventoryID, payload.quantity, payload.unitCost))
            
            conn.commit()
        return {"message": "Inventory imported successfully"}
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in import_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)

@router.post("/inventory/export", status_code=status.HTTP_201_CREATED)
def export_inventory(payload: InventoryExport):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Kiểm tra số lượng tồn kho
            cursor.execute(queries.SELECT_STOCK_QUANTITY_FOR_EXPORT, (payload.inventoryID,))
            result = cursor.fetchone()
            if not result or result['stockQuantity'] < payload.quantity:
                raise HTTPException(status_code=400, detail="Insufficient inventory")
            
            # Thêm vào stores với roleStore = 'Export' (số lượng âm)
            cursor.execute(queries.INSERT_STORE_FOR_EXPORT, (payload.productID, payload.inventoryID, payload.exportDate or datetime.datetime.now(), -payload.quantity))
            
            # Cập nhật stock quantity
            cursor.execute(queries.UPDATE_INVENTORY_FOR_EXPORT, (payload.quantity, payload.inventoryID))
            
            conn.commit()
        return {"message": "Inventory exported successfully"}
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in export_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)

@router.post("/inventory/stocktaking", status_code=status.HTTP_201_CREATED)
def stocktaking(payload: Stocktaking):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Lấy số lượng hiện tại
            cursor.execute(queries.SELECT_STOCK_QUANTITY_FOR_STOCKTAKING, (payload.inventoryID,))
            current = cursor.fetchone()
            if not current:
                raise HTTPException(status_code=404, detail="Inventory not found")
            
            difference = payload.actualQuantity - current['stockQuantity']
            
            # Cập nhật số lượng thực tế
            cursor.execute(queries.UPDATE_INVENTORY_FOR_STOCKTAKING, (payload.actualQuantity, payload.inventoryID))
            
            # Ghi lại lịch sử kiểm kê vào stores
            if difference != 0:
                cursor.execute(queries.INSERT_STORE_FOR_STOCKTAKING, (payload.productID, payload.inventoryID, payload.stocktakingDate or datetime.datetime.now(), difference))
            
            conn.commit()
        return {"message": "Stocktaking completed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in stocktaking: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)
