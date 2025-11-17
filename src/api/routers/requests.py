from fastapi import APIRouter, HTTPException, status
import logging

from ..db import fetchall_sql, execute_sql
from ..models.request import Request
from .. import queries

router = APIRouter()

@router.get("/requests")
def get_requests():
    try:
        return fetchall_sql(queries.SELECT_REQUESTS)
    except Exception as e:
        logging.error(f"Error in get_request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/requests/{id}")
def get_request(id: int):
    try:
        return fetchall_sql(queries.SELECT_REQUEST_BY_ID, (id,))
    except Exception as e:
        logging.error(f"Error in get_request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/requests", status_code=status.HTTP_201_CREATED)
def create_request(payload: Request):
    try:
        request_id = execute_sql(queries.INSERT_REQUEST, (
            payload.orderID, payload.productID, payload.quantityOrdered, payload.discount, payload.note
        ))
        return {"message": "Request created", "requestID": request_id}
    except Exception as e:
        logging.error(f"Error in create_request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/requests/{id}")
def update_request(id: int, payload: Request):
    try:
        execute_sql(queries.UPDATE_REQUEST, (
            payload.orderID, payload.productID, payload.quantityOrdered, payload.discount, payload.note, id
        ))
        return {"message": "Request updated successfully"}
    except Exception as e:
        logging.error(f"Error in update_request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/requests/{id}")
def delete_request(id: int):
    try:
        execute_sql(queries.DELETE_REQUEST, (id,))
        return {"message": "Request deleted"}
    except Exception as e:
        logging.error(f"Error in delete_request: {e}")
        raise HTTPException(status_code=500, detail=str(e))