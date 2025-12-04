from fastapi import APIRouter, HTTPException, status
import logging

from ..db import fetchall_sql, execute_sql
from ..models.payment import Payment
from .. import queries

router = APIRouter()

@router.get("/payments")
def get_payments():
    try:
        return fetchall_sql(queries.SELECT_PAYMENTS)
    except Exception as e:
        logging.error(f"Error in get_payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payments", status_code=status.HTTP_201_CREATED)
def create_payment(payload: Payment):
    try:
        execute_sql(queries.INSERT_PAYMENT, (
            payload.orderID,
            payload.tran=sactionAmount,
            payload.paymentMethod,
            payload.transactionStatus
        ))
        return {"message": "Payment created"}
    except Exception as e:
        logging.error(f"Error in create_payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/payments/{paymentID}")
def update_payment(paymentID: int, payload: Payment):
    try:
        execute_sql(queries.UPDATE_PAYMENT, (
            payload.orderID,
            payload.transactionAmount,
            payload.paymentMethod,
            payload.transactionStatus,
            paymentID
        ))
        return {"message": "Payment updated successfully"}
    except Exception as e:
        logging.error(f"Error in update_payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/payments/{id}")
def delete_payment(id: int):
    try:
        execute_sql(queries.DELETE_PAYMENT, (id,))
        return {"message": "Payment deleted"}
    except Exception as e:
        logging.error(f"Error in delete_payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))
