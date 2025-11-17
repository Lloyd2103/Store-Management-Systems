from fastapi import APIRouter, HTTPException, status
import logging

from ..db import fetchall_sql, execute_sql
from ..models.staff import Staff
from .. import queries

router = APIRouter()

@router.get("/staffs")
def get_staff():
    try:
        return fetchall_sql(queries.SELECT_STAFFS)
    except Exception as e:
        logging.error(f"Error in get_staff: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/staffs", status_code=status.HTTP_201_CREATED)
def create_staff(payload: Staff):
    try:
        execute_sql(queries.INSERT_STAFF, (
            payload.staffName,
            payload.position,
            payload.phone,
            payload.email,
            payload.address,
            payload.managerID,
            payload.salary
        ))
    except Exception as e:
        logging.error(f"Error in create_staff: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/staffs/{id}")
def update_staff(id: int, payload: Staff):
    try:
        execute_sql(queries.UPDATE_STAFF, (
            payload.staffName,
            payload.position,
            payload.phone,
            payload.email,
            payload.address,
            payload.managerID,
            payload.salary,
            id
        ))
        return {"message": "Staff updated successfully"}
        
    except Exception as e:
        logging.error(f"Error in update_staff: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/staffs/{id}")
def delete_staff(id: int):
    try:
        execute_sql(queries.DELETE_STAFF, (id,))
        return {"message": "Staff deleted"}
    except Exception as e:
        logging.error(f"Error in delete_staff: {e}")
        raise HTTPException(status_code=500, detail=str(e))
