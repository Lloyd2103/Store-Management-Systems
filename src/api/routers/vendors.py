from fastapi import APIRouter, HTTPException, status
import logging

from ..db import fetchall_sql, execute_sql, get_connection, safe_close_connection
from ..models.vendor import Vendor
from .. import queries

router = APIRouter()

def check_vendor_usage(vendor_id: int) -> dict:
    """Kiểm tra xem vendor có đang được sử dụng trong supplies không"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(queries.CHECK_VENDOR_IN_SUPPLIES, (vendor_id,))
            supplies_count = cursor.fetchone()['count']
            
            return {
                'has_supplies': supplies_count > 0,
                'supplies_count': supplies_count,
                'can_delete': supplies_count == 0
            }
    finally:
        safe_close_connection(conn)

@router.get("/vendors")
def get_vendors():
    try:
        return fetchall_sql(queries.SELECT_VENDORS)
    except Exception as e:
        logging.error(f"Error in get_vendors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vendors/{id}/products")
def get_vendor_products(id: int):
    """Lấy tất cả products được supply bởi vendor"""
    try:
        return fetchall_sql(queries.SELECT_VENDOR_PRODUCTS, (id,))
    except Exception as e:
        logging.error(f"Error in get_vendor_products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vendors", status_code=status.HTTP_201_CREATED)
def create_vendor(payload: Vendor):
    try:
        vendor_id = execute_sql(queries.INSERT_VENDOR, (
            payload.vendorName,
            payload.contactName,
            payload.phone,
            payload.email,
            payload.address
        ))
        return {"message": "Vendor created", "vendorID": vendor_id}
    except Exception as e:
        logging.error(f"Error in create_vendor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/vendors/{id}")
def update_vendor(id: int, payload: Vendor):
    try:
        execute_sql(queries.UPDATE_VENDOR, (
            payload.vendorName,
            payload.contactName,
            payload.phone,
            payload.email,
            payload.address,
            id
        ))
    except Exception as e:
        logging.error(f"Error in update_vendor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/vendors/{id}")
def delete_vendor(id: int):
    try:
        # Kiểm tra xem vendor có đang được sử dụng không
        usage = check_vendor_usage(id)
        
        if not usage['can_delete']:
            raise HTTPException(
                status_code=400, 
                detail=f"Không thể xóa nhà cung cấp này vì đang được sử dụng trong {usage['supplies_count']} bản ghi cung cấp sản phẩm"
            )
        
        execute_sql(queries.DELETE_VENDOR, (id,))
        return {"message": "Vendor deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in delete_vendor: {e}")
        raise HTTPException(status_code=500, detail=str(e))
