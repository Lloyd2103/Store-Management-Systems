from fastapi import APIRouter, HTTPException, status
import logging

from ..db import fetchall_sql, execute_sql, get_connection, safe_close_connection
from ..models.vendor import Vendor
from .. import queries

router = APIRouter()

@router.get("/vendors")
def get_vendors():
    try:
        return fetchall_sql(queries.SELECT_VENDORS)
    except Exception as e:
        logging.error(f"Error in get_vendors: {e}")
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
            
            payload.address,
            id
        ))
    except Exception as e:
        logging.error(f"Error in update_vendor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/vendors/{id}")
def delete_vendor(id: int):
    try:
        execute_sql(queries.DELETE_VENDOR, (id,))
        return {"message": "Vendor deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in delete_vendor: {e}")
        raise HTTPException(status_code=500, detail=str(e))
