from typing import Optional
from fastapi import APIRouter, HTTPException, status
import logging

from ..db import fetchall_sql, execute_sql
from ..models.customer import Customer
from .. import queries

router = APIRouter()

@router.get("/customers")
def get_customers(search: Optional[str] = None):
    try:
        if search:
            search_pattern = f"%{search}%"
            rows = fetchall_sql(queries.SELECT_CUSTOMERS_SEARCH, (search_pattern, search_pattern, search_pattern))
        else:
            rows = fetchall_sql(queries.SELECT_CUSTOMERS)
        return rows
    except Exception as e:
        logging.error(f"Error in get_customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customers/{id}")
def get_customer(id: int):
    try:
        rows = fetchall_sql(queries.SELECT_CUSTOMER_BY_ID, (id,))
        if not rows:
            raise HTTPException(status_code=404, detail="Customer not found")
        return rows[0]
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in get_customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/customers", status_code=status.HTTP_201_CREATED)
def create_customer(payload: Customer):
    try:
        execute_sql(queries.INSERT_CUSTOMER, (payload.customerName, payload.phone, payload.email, payload.address, payload.postalCode))
        return {"message": "Customer added"}
    except Exception as e:
        logging.error(f"Error in add_customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/customers/{id}")
def update_customer(id: int, payload: Customer):
    try:
        execute_sql(queries.UPDATE_CUSTOMER, (payload.customerName, payload.phone, payload.email, payload.address, payload.postalCode, id))
        return {"message": "Customer updated successfully"}
    except Exception as e:
        logging.error(f"Error in update_customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/customers/{id}")
def delete_customer(id: int):
    try:
        execute_sql(queries.DELETE_CUSTOMER, (id,))
        return {"message": "Customer deleted"}
    except Exception as e:
        logging.error(f"Error in delete_customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
