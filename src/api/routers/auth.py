from fastapi import APIRouter, HTTPException, status
import logging
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import get_connection, safe_close_connection
from ..models.auth import RegisterModel, RegisterStaffModel, LoginModel
from .. import queries

router = APIRouter()

@router.post("/register/customer", status_code=status.HTTP_201_CREATED)
def register_customer(payload: RegisterModel):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(queries.SELECT_CUSTOMER_FOR_AUTH, (payload.phone, payload.email))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Phone or email already exists")

            password_hash = generate_password_hash(payload.password)
            cursor.execute(queries.INSERT_CUSTOMER_FOR_AUTH, (
                payload.customerName, payload.phone, payload.email,
                payload.address, payload.postalCode, payload.customerType,
                payload.loyalPoint, payload.loyalLevel, password_hash
            ))
            conn.commit()
        return {"message": "Customer registration successful"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in register_customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)



# staff registration (should be protected in production)
@router.post("/register/staff", status_code=status.HTTP_201_CREATED)
def register_staff(payload: RegisterStaffModel):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(queries.SELECT_STAFF_FOR_AUTH, (payload.phone, payload.email))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Staff phone or email already exists")

            password_hash = generate_password_hash(payload.password)
            cursor.execute(queries.INSERT_STAFF_FOR_AUTH, (
                payload.staffName, payload.position, payload.phone,
                payload.email, payload.address, payload.managerID,
                payload.salary, password_hash
            ))
            conn.commit()
        return {"message": "Staff registration successful"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in register_staff: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)


@router.post("/login/customer")
def login_customer(payload: LoginModel):
    conn = None
    try:
        identifier = payload.identifier
        password = payload.password
        if not identifier or not password:
            raise HTTPException(status_code=400, detail="Missing identifier or password")

        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(queries.LOGIN_CUSTOMER, (identifier, identifier))
            user = cursor.fetchone()

        if user and check_password_hash(user.get('passwordHash') or user.get('password_hash', ""), password):
            user.pop('passwordHash', None)
            user.pop('password_hash', None)
            return {"message": "Login successful", "customer": user}
        else:
            raise HTTPException(status_code=401, detail="Invalid email/phone or password")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in login_customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)
        
@router.post("/login/staff")
def login_staff(payload: LoginModel):
    conn = None
    try:
        identifier = payload.identifier
        password = payload.password
        if not identifier or not password:
            raise HTTPException(status_code=400, detail="Missing identifier or password")

        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(queries.LOGIN_STAFF, (identifier, identifier))
            user = cursor.fetchone()

        if user and check_password_hash(user.get('passwordHash') or user.get('password_hash', ""), password):
            user.pop('passwordHash', None)
            user.pop('password_hash', None)
            return {"message": "Login successful", "staff": user}
        else:
            raise HTTPException(status_code=401, detail="Invalid email/phone or password")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in login_staff: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)
