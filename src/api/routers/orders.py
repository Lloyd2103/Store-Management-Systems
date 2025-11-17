from typing import Optional
from fastapi import APIRouter, HTTPException, status
import logging

from ..db import get_connection, safe_close_connection, fetchall_sql, execute_sql
from ..models.order import Order, OrderCheckoutModel
from .. import queries

router = APIRouter()

@router.get("/orders")
def get_orders(search: Optional[str] = None, status: Optional[str] = None, customer_id: Optional[int] = None):
    try:
        conditions = []
        params = []
        if search:
            conditions.append("orderID LIKE %s")
            params.append(f"%{search}%")
        if status:
            conditions.append("orderStatus = %s")
            params.append(status)
        if customer_id:
            conditions.append("customerID = %s")
            params.append(customer_id)
        
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT * FROM tbl_order{where_clause} ORDER BY orderDate DESC"
        return fetchall_sql(query, tuple(params) if params else ())
    except Exception as e:
        logging.error(f"Error in get_orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{id}")
def get_order(id: int):
    try:
        return fetchall_sql(queries.SELECT_ORDER_BY_CUSTOMER_ID, (id,))
    except Exception as e:
        logging.error(f"Error in get_order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(payload: Order):
    try:
        order_id = execute_sql(queries.INSERT_ORDER, (
            payload.totalAmount,
            payload.orderStatus,
            payload.paymentDate,
            payload.paymentStatus,
            payload.pickupMethod,
            payload.shippedDate,
            payload.shippedStatus,
            payload.customerID,
            payload.staffID
        ))
        return {"message": "Order created", "orderID": order_id}
    except Exception as e:
        logging.error(f"Error in create_order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/orders/{id}")
def update_order(id: int, payload: Order):
    try:
        execute_sql(queries.UPDATE_ORDER, (
            payload.orderStatus,
            payload.paymentStatus,
            payload.pickupMethod,
            payload.shippedStatus,
            payload.shippedDate,
            payload.paymentDate,
            payload.totalAmount,
            id
        ))
        return {"message": "Order updated successfully"}
    except Exception as e:
        logging.error(f"Error in update_order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/orders/{id}")
def delete_order(id: int):
    try:
        execute_sql(queries.DELETE_ORDER, (id,))
        return {"message": "Order deleted"}
    except Exception as e:
        logging.error(f"Error in delete_order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/order/checkout")
def order_checkout(payload: OrderCheckoutModel):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:

            # 1. Insert ORDER
            cursor.execute(queries.CHECKOUT_INSERT_ORDER, (
                sum([p["quantity"] * p["priceEach"] for p in payload.products]),
                None,
                payload.paymentStatus,
                payload.pickupMethod,
                payload.shippedDate,
                payload.shippedStatus,
                payload.customerID,
                payload.staffID
            ))
            
            order_id = conn.insert_id()

            # 2. Insert REQUEST for each product
            for p in payload.products:
                cursor.execute(queries.CHECKOUT_INSERT_REQUEST, (order_id, p["productID"], p["quantity"], 0, ""))
            # 3. Insert PAYMENT if online
            if payload.paymentMethod in ("BankTransfer", "Voucher"):
                cursor.execute(queries.CHECKOUT_INSERT_PAYMENT, (
                    order_id,
                    sum([p["quantity"] * p["priceEach"] for p in payload.products]),
                    payload.paymentMethod
                ))
            conn.commit()
            return {"message": "Checkout successful", "orderID": order_id}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)
