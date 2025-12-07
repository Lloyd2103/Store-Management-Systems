import datetime
from fastapi import APIRouter, HTTPException, status
import logging

from ..db import fetchall_sql, execute_sql, get_connection, safe_close_connection
from ..models.supply import Supply
from .. import queries

router = APIRouter()

@router.get("/supplies")
def get_supply():
    try:
        return fetchall_sql(queries.SELECT_SUPPLIES)
    except Exception as e:
        logging.error(f"Error in get_supply: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supplies/product/{product_id}")
def get_supplies_by_product(product_id: int):
    """Lấy tất cả supplies của một product"""
    try:
        return fetchall_sql(queries.SELECT_SUPPLIES_BY_PRODUCT, (product_id,))
    except Exception as e:
        logging.error(f"Error in get_supplies_by_product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supplies/{vendor_id}")
def get_supplies_by_vendor(vendor_id: int):
    """Lấy tất cả supplies của một vendor"""
    try:
        return fetchall_sql(queries.SELECT_SUPPLIES_BY_VENDOR, (vendor_id,))
    except Exception as e:
        logging.error(f"Error in get_supplies_by_vendor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/supplies", status_code=status.HTTP_201_CREATED)
def create_supply(payload: Supply):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Kiểm tra product và vendor có tồn tại không
            cursor.execute(queries.SELECT_PRODUCT_FOR_SUPPLY, (payload.productID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Product with ID {payload.productID} not found")
            
            cursor.execute(queries.SELECT_VENDOR_FOR_SUPPLY, (payload.vendorID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Vendor with ID {payload.vendorID} not found")
            
            # Tạo supplies relationship
            cursor.execute(queries.INSERT_SUPPLY, (
                payload.productID, 
                payload.vendorID, 
                payload.supplyDate or datetime.datetime.now(), 
                payload.quantitySupplier, 
                payload.handledBy
            ))
            
            conn.commit()
            supply_id = cursor.lastrowid
        return {"message": "Supply created", "supplyID": supply_id}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in create_supply: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)
    
@router.put("/supplies/{id}")
def update_supply(id: int, payload: Supply):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Kiểm tra product và vendor có tồn tại không
            cursor.execute(queries.SELECT_PRODUCT_FOR_SUPPLY, (payload.productID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Product with ID {payload.productID} not found")
            
            cursor.execute(queries.SELECT_VENDOR_FOR_SUPPLY, (payload.vendorID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Vendor with ID {payload.vendorID} not found")
            
            # Cập nhật supplies relationship
            cursor.execute(queries.UPDATE_SUPPLY, (
                payload.productID, 
                payload.vendorID, 
                payload.supplyDate or datetime.datetime.now(), 
                payload.quantitySupplier, 
                payload.handledBy, 
                id
            ))
            
            conn.commit()
        return {"message": "Supply updated successfully"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in update_supply: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)
@router.delete("/supplies/{id}")
def delete_supply(id: int):
    try:
        execute_sql(queries.DELETE_SUPPLY, (id,))
        return {"message": "Supply deleted"}
    except Exception as e:
        logging.error(f"Error in delete_supply: {e}")
        raise HTTPException(status_code=500, detail=str(e))
