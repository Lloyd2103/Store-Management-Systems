from typing import Optional, List, Any
import datetime
import logging
import pymysql
from pymysql.cursors import DictCursor
from werkzeug.security import generate_password_hash, check_password_hash

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import ORJSONResponse

# Import config
from config import (
    SERVER_HOST, SERVER_PORT, SERVER_RELOAD,
    DB_CONFIG as CONFIG_DB_CONFIG,
    CORS_ALLOW_ORIGINS, CORS_ALLOW_CREDENTIALS, CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS,
    LOG_LEVEL
)

# Logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))

# FastAPI app
app = FastAPI(default_response_class=ORJSONResponse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# ===== DATABASE CONFIG =====
# Thêm cursorclass vào config
DB_CONFIG = CONFIG_DB_CONFIG.copy()
DB_CONFIG["cursorclass"] = DictCursor

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def safe_close_connection(conn):
    if conn is not None:
        try:
            if getattr(conn, "open", True):
                conn.close()
        except Exception as e:
            logging.error(f"Error closing connection: {e}")


class RegisterModel(BaseModel):
    customerName: str
    phone: str
    password: str
    address: str
    postalCode: Optional[str] = None
    email: Optional[str] = None
    customerType: Optional[str] = "Individual"
    loyalPoint: Optional[int] = 0
    loyalLevel: Optional[str] = "New"

class LoginModel(BaseModel):
    identifier: str
    password: str

class RegisterCustomerModel(BaseModel):
    customerName: str
    phone: str
    password: str
    address: str
    postalCode: Optional[str] = None
    email: Optional[str] = None
    customerType: Optional[str] = "Individual"
    loyalPoint: Optional[int] = 0
    loyalLevel: Optional[str] = "New"

class RegisterStaffModel(BaseModel):
    staffName: str
    position: Optional[str] = None
    phone: str
    password: str
    email: Optional[str] = None
    address: Optional[str] = None
    managerID: Optional[int] = None
    salary: Optional[float] = None

class Customer(BaseModel):
    customerName: str
    phone: str
    email: Optional[str] = None
    address: str
    postalCode: Optional[str] = None

class Order(BaseModel):
    orderDate: Optional[datetime.datetime] = None
    totalAmount: Optional[float] = 0
    orderStatus: Optional[str] = "Pending"
    paymentDate: Optional[str] = None
    paymentStatus: Optional[str] = "Unpaid"
    pickupMethod: Optional[str] = "Ship"
    shippedDate: Optional[str] = None
    shippedStatus: Optional[str] = "In Process"
    customerID: Optional[int] = None
    staffID: Optional[int] = None

class OrderCheckoutModel(BaseModel):
    customerID: int
    staffID: Optional[int] = None
    paymentMethod: str
    products: List[dict]  # [{productID, quantity, priceEach}]
    pickupMethod: str
    orderStatus: str
    paymentStatus: str
    shippedStatus: str
    shippedDate: Optional[str] = None

class Payment(BaseModel):
    orderID: int
    transactionAmount: float
    paymentMethod: Optional[str] = None
    transactionDate: Optional[datetime.datetime] = None
    transactionStatus: Optional[str] = None

class Product(BaseModel):
    productName: str
    priceEach: float
    productLine: str
    productScale: str
    productBrand: str
    productDiscription: str
    warrantyPeriod: int
    MSRP: float

class Staff(BaseModel):
    staffName: str
    position: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    managerID: Optional[int] = None
    salary: Optional[float] = None

class Vendor(BaseModel):
    vendorName: str
    contactName: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None

class Inventory(BaseModel):
    inventoryID: int
    warehouse: str
    maxStockLevel: int
    stockQuantity: int
    unitCost: float
    lastedUpdate: Optional[datetime.datetime] = None
    inventoryNote: Optional[str] = None
    inventoryStatus: Optional[str] = "Active"

class Request(BaseModel):
    orderID: int
    productID: int
    quantityOrdered: int
    discount: Optional[float] = 0
    note: str

class Store(BaseModel):
    productID: int
    inventoryID: int
    storeDate: Optional[datetime.datetime] = None
    quantityStore: int
    roleStore: Optional[str] = None

class Supply(BaseModel):
    productID: int
    vendorID: int
    supplyDate: Optional[datetime.datetime] = None
    quantitySupplier: int
    note: str

class Category(BaseModel):
    categoryName: str
    description: Optional[str] = None

class CustomerDebt(BaseModel):
    customerID: int
    debtAmount: float
    debtDate: Optional[datetime.datetime] = None
    note: Optional[str] = None

class InventoryImport(BaseModel):
    productID: int
    inventoryID: int
    quantity: int
    importDate: Optional[datetime.datetime] = None
    unitCost: float
    note: Optional[str] = None

class InventoryExport(BaseModel):
    productID: int
    inventoryID: int
    quantity: int
    exportDate: Optional[datetime.datetime] = None
    reason: Optional[str] = None
    note: Optional[str] = None

class Stocktaking(BaseModel):
    inventoryID: int
    productID: int
    actualQuantity: int
    stocktakingDate: Optional[datetime.datetime] = None
    note: Optional[str] = None

# ===== HELPERS =====
def fetchall_sql(query: str, params: tuple = ()):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            
            cursor.execute(query, params)
            return cursor.fetchall()
    finally:
        safe_close_connection(conn)

def execute_sql(query: str, params: tuple = ()):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            #print("Executing SQL:", query, "with params:", params)
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    finally:
        safe_close_connection(conn)

# ===== VALIDATION HELPERS =====
def check_product_usage(product_id: int) -> dict:
    """Kiểm tra xem product có đang được sử dụng trong orders, stores, supplies không"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Kiểm tra trong orders (tbl_requests)
            cursor.execute("SELECT COUNT(*) as count FROM tbl_requests WHERE productID = %s", (product_id,))
            orders_count = cursor.fetchone()['count']
            
            # Kiểm tra trong stores
            cursor.execute("SELECT COUNT(*) as count FROM tbl_stores WHERE productID = %s", (product_id,))
            stores_count = cursor.fetchone()['count']
            
            # Kiểm tra trong supplies
            cursor.execute("SELECT COUNT(*) as count FROM tbl_supplies WHERE productID = %s", (product_id,))
            supplies_count = cursor.fetchone()['count']
            
            return {
                'has_orders': orders_count > 0,
                'orders_count': orders_count,
                'has_stores': stores_count > 0,
                'stores_count': stores_count,
                'has_supplies': supplies_count > 0,
                'supplies_count': supplies_count,
                'can_delete': orders_count == 0 and stores_count == 0 and supplies_count == 0
            }
    finally:
        safe_close_connection(conn)

def check_vendor_usage(vendor_id: int) -> dict:
    """Kiểm tra xem vendor có đang được sử dụng trong supplies không"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM tbl_supplies WHERE vendorID = %s", (vendor_id,))
            supplies_count = cursor.fetchone()['count']
            
            return {
                'has_supplies': supplies_count > 0,
                'supplies_count': supplies_count,
                'can_delete': supplies_count == 0
            }
    finally:
        safe_close_connection(conn)

def check_inventory_usage(inventory_id: int) -> dict:
    """Kiểm tra xem inventory có đang được sử dụng trong stores không"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM tbl_stores WHERE inventoryID = %s", (inventory_id,))
            stores_count = cursor.fetchone()['count']
            
            return {
                'has_stores': stores_count > 0,
                'stores_count': stores_count,
                'can_delete': stores_count == 0
            }
    finally:
        safe_close_connection(conn)



# ===== CUSTOMERS =====
@app.get("/customers")
def get_customers(search: Optional[str] = None):
    try:
        if search:
            query = """
                SELECT customerID, customerName, phone, email, address, postalCode, customerType, loyalPoint, loyalLevel 
                FROM tbl_customer 
                WHERE customerName LIKE %s OR phone LIKE %s OR email LIKE %s
            """
            search_pattern = f"%{search}%"
            rows = fetchall_sql(query, (search_pattern, search_pattern, search_pattern))
        else:
            rows = fetchall_sql(
                "SELECT customerID, customerName, phone, email, address, postalCode, customerType, loyalPoint, loyalLevel FROM tbl_customer"
            )
        return rows
    except Exception as e:
        logging.error(f"Error in get_customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customers/{id}")
def get_customer(id: int):
    try:
        rows = fetchall_sql(
            "SELECT customerID, customerName, phone, email, address, postalCode, customerType, loyalPoint, loyalLevel FROM tbl_customer WHERE customerID = %s",
            (id,)
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Customer not found")
        return rows[0]
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in get_customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/customers", status_code=status.HTTP_201_CREATED)
def create_customer(payload: Customer):
    try:
        sql = "INSERT INTO tbl_customer (customerName, phone, email, address, postalCode) VALUES (%s, %s, %s, %s, %s)" #lưu query vào file riêng
        execute_sql(sql, (payload.customerName, payload.phone, payload.email, payload.address, payload.postalCode))
        return {"message": "Customer added"}
    except Exception as e:
        logging.error(f"Error in add_customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/customers/{id}")
def update_customer(id: int, payload: Customer):
    try:
        sql = "UPDATE tbl_customer SET customerName=%s, phone=%s, email=%s, address=%s, postalCode=%s WHERE customerID=%s"
        execute_sql(sql, (payload.customerName, payload.phone, payload.email, payload.address, payload.postalCode, id))
        return {"message": "Customer updated successfully"}
    except Exception as e:
        logging.error(f"Error in update_customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/customers/{id}")
def delete_customer(id: int):
    try:
        execute_sql("DELETE FROM tbl_customer WHERE customerID = %s", (id,))
        return {"message": "Customer deleted"}
    except Exception as e:
        logging.error(f"Error in delete_customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# ===== PRODUCTS =====
@app.get("/products")
def get_products(search: Optional[str] = None, category: Optional[str] = None):
    try:
        if search or category:
            conditions = []
            params = []
            if search:
                conditions.append("(productName LIKE %s OR productBrand LIKE %s OR productLine LIKE %s)")
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            if category:
                conditions.append("productLine = %s")
                params.append(category)
            where_clause = " WHERE " + " AND ".join(conditions)
            query = f"SELECT * FROM tbl_product{where_clause}"
            return fetchall_sql(query, tuple(params))
        else:
            return fetchall_sql("SELECT * FROM tbl_product")
    except Exception as e:
        logging.error(f"Error in get_products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products/{id}")
def get_product(id: int):
    try:
        rows = fetchall_sql("SELECT * FROM tbl_product WHERE productID = %s", (id,))
        if not rows:
            raise HTTPException(status_code=404, detail="Product not found")
        return rows[0]
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in get_product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{id}/inventory")
def get_product_inventory(id: int):
    """Lấy thông tin inventory của một product"""
    try:
        query = """
            SELECT 
                i.*,
                s.storeDate,
                s.quantityStore,
                s.roleStore
            FROM tbl_inventory i
            INNER JOIN tbl_stores s ON i.inventoryID = s.inventoryID
            WHERE s.productID = %s
            ORDER BY s.storeDate DESC
        """
        return fetchall_sql(query, (id,))
    except Exception as e:
        logging.error(f"Error in get_product_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{id}/suppliers")
def get_product_suppliers(id: int):
    """Lấy thông tin suppliers của một product"""
    try:
        query = """
            SELECT 
                v.*,
                s.supplyDate,
                s.quantitySupplier,
                s.note as supplyNote
            FROM tbl_vendor v
            INNER JOIN tbl_supplies s ON v.vendorID = s.vendorID
            WHERE s.productID = %s
            ORDER BY s.supplyDate DESC
        """
        return fetchall_sql(query, (id,))
    except Exception as e:
        logging.error(f"Error in get_product_suppliers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(payload: Product):
    try:
        sql = """
            INSERT INTO tbl_product (
                productName, priceEach, productLine, productScale,
                productBrand, productDiscription, warrantyPeriod, MSRP
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        product_id = execute_sql(sql, (
            payload.productName,
            payload.priceEach,
            payload.productLine,
            payload.productScale,
            payload.productBrand,
            payload.productDiscription,
            payload.warrantyPeriod,
            payload.MSRP
        ))
        return {"message": "Product created", "productID": product_id}
        
    except Exception as e:
        logging.error(f"Error in create_product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/products/{id}")
def update_product(id: int, payload: Product):
    try:
        sql = """
            UPDATE tbl_product
            SET productName=%s, priceEach=%s, productLine=%s, productScale=%s,
                productBrand=%s, productDiscription=%s, warrantyPeriod=%s, MSRP=%s
            WHERE productID=%s
        """
        
        print( (
            payload.productName,
            payload.priceEach,
            payload.productLine,
            payload.productScale,
            payload.productBrand,
            payload.productDiscription,
            payload.warrantyPeriod,
            payload.MSRP,
            id
        ))
        execute_sql(sql, (
            payload.productName,
            payload.priceEach,
            payload.productLine,
            payload.productScale,
            payload.productBrand,
            payload.productDiscription,
            payload.warrantyPeriod,
            payload.MSRP,
            id
        ))
        return {"message": "Product updated successfully"}
    except Exception as e:
        logging.error(f"Error in update_product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/products/{id}")
def delete_product(id: int):
    try:
        # Kiểm tra xem product có đang được sử dụng không
        usage = check_product_usage(id)
        
        if not usage['can_delete']:
            messages = []
            if usage['has_orders']:
                messages.append(f"{usage['orders_count']} đơn hàng")
            if usage['has_stores']:
                messages.append(f"{usage['stores_count']} bản ghi kho")
            if usage['has_supplies']:
                messages.append(f"{usage['supplies_count']} bản ghi nhà cung cấp")
            
            raise HTTPException(
                status_code=400, 
                detail=f"Không thể xóa sản phẩm này vì đang được sử dụng trong: {', '.join(messages)}"
            )
        
        execute_sql("DELETE FROM tbl_product WHERE productID = %s", (id,))
        return {"message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in delete_product: {e}")
        raise HTTPException(status_code=500, detail=str(e))




# ===== ORDERS =====

    
@app.get("/orders")
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

@app.get("/orders/{id}")
def get_order(id: int):
    try:
        return fetchall_sql("SELECT * FROM tbl_order WHERE customerID = %s", (id,))
    except Exception as e:
        logging.error(f"Error in get_order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(payload: Order):
    try:
        sql = """
            INSERT INTO tbl_order (
                totalAmount, orderStatus, paymentDate, paymentStatus,
                pickupMethod, shippedDate, shippedStatus, customerID, staffID
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        order_id = execute_sql(sql, (
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

@app.put("/orders/{id}")
def update_order(id: int, payload: Order):
    try:
        sql = """
            UPDATE tbl_order
            SET orderStatus=%s, paymentStatus=%s, pickupMethod=%s,
                shippedStatus=%s, shippedDate=%s, paymentDate=%s, totalAmount=%s
            WHERE orderID=%s
        """
        execute_sql(sql, (
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


@app.delete("/orders/{id}")
def delete_order(id: int):
    try:
        execute_sql("DELETE FROM tbl_order WHERE orderID = %s", (id,))
        return {"message": "Order deleted"}
    except Exception as e:
        logging.error(f"Error in delete_order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/order/checkout")
def order_checkout(payload: OrderCheckoutModel):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:

            # 1. Insert ORDER
            cursor.execute("""
                INSERT INTO tbl_order (
                    totalAmount, orderStatus, paymentDate, paymentStatus,
                    pickupMethod, shippedDate, shippedStatus, customerID, staffID
                ) VALUES (%s,'Pending',%s,%s,%s,%s,%s,%s,%s)
            """, (
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
                cursor.execute("""
                    INSERT INTO tbl_requests (orderID, productID, quantityOrdered, discount, note)
                    VALUES (%s,%s,%s,%s,%s)
                """, (order_id, p["productID"], p["quantity"], 0, ""))
            # 3. Insert PAYMENT if online
            if payload.paymentMethod in ("BankTransfer", "Voucher"):
                cursor.execute("""
                    INSERT INTO tbl_payment (orderID, transactionAmount, paymentMethod, transactionDate, transactionStatus)
                    VALUES (%s,%s,%s,NOW(),'Pending')
                """, (
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

# ===== PAYMENTS =====
@app.get("/payments")
def get_payments():
    try:
        return fetchall_sql("SELECT * FROM tbl_payment")
    except Exception as e:
        logging.error(f"Error in get_payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/payments", status_code=status.HTTP_201_CREATED)
def create_payment(payload: Payment):
    try:
        sql = """
            INSERT INTO tbl_payment (orderID, transactionAmount, paymentMethod, transactionDate, transactionStatus)
            VALUES (%s, %s, %s, NOW(), %s)
        """
        execute_sql(sql, (
            payload.orderID,
            payload.transactionAmount,
            payload.paymentMethod,
            payload.transactionStatus
        ))
        return {"message": "Payment created"}
    except Exception as e:
        logging.error(f"Error in create_payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/payments/{paymentID}")
def update_payment(paymentID: int, payload: Payment):
    try:
        sql = """
            UPDATE tbl_payment
            SET orderID=%s, transactionAmount=%s, paymentMethod=%s, transactionDate=NOW(), transactionStatus=%s
            WHERE paymentID=%s
        """
        execute_sql(sql, (
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

@app.delete("/payments/{id}")
def delete_payment(id: int):
    try:
        execute_sql("DELETE FROM tbl_payment WHERE paymentID = %s", (id,))
        return {"message": "Payment deleted"}
    except Exception as e:
        logging.error(f"Error in delete_payment: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 

# ===== STAFF =====
@app.get("/staffs")
def get_staff():
    try:
        return fetchall_sql("SELECT staffID, staffName, position, phone, email, address, managerID, salary FROM tbl_staff") #
    except Exception as e:
        logging.error(f"Error in get_staff: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/staffs", status_code=status.HTTP_201_CREATED)
def create_staff(payload: Staff):
    try:
        sql = """
            INSERT INTO tbl_staff (staffName, position, phone, email, address, managerID, salary)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        execute_sql(sql, (
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

@app.put("/staffs/{id}")
def update_staff(id: int, payload: Staff):
    try:
        sql = """
            UPDATE tbl_staff SET staffName=%s, position=%s, phone=%s, email=%s, address=%s, managerID=%s, salary=%s WHERE staffID=%s
        """
        execute_sql(sql, (
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

@app.delete("/staffs/{id}")
def delete_staff(id: int):
    try:
        sql = f"DELETE FROM tbl_staff WHERE staffID = %s"
        execute_sql(sql, (id,))
        return {"message": "Staff deleted"}
    except Exception as e:
        logging.error(f"Error in delete_staff: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# ===== VENDORS =====
@app.get("/vendors")
def get_vendors():
    try:
        # Lấy vendors kèm thông tin số lượng products đang được supply
        query = """
            SELECT 
                v.*,
                COUNT(DISTINCT s.productID) as productCount
            FROM tbl_vendor v
            LEFT JOIN tbl_supplies s ON v.vendorID = s.vendorID
            GROUP BY v.vendorID
            ORDER BY v.vendorID
        """
        return fetchall_sql(query)
    except Exception as e:
        logging.error(f"Error in get_vendors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vendors/{id}/products")
def get_vendor_products(id: int):
    """Lấy tất cả products được supply bởi vendor"""
    try:
        query = """
            SELECT 
                p.*,
                s.supplyDate,
                s.quantitySupplier,
                s.note as supplyNote
            FROM tbl_product p
            INNER JOIN tbl_supplies s ON p.productID = s.productID
            WHERE s.vendorID = %s
            ORDER BY s.supplyDate DESC
        """
        return fetchall_sql(query, (id,))
    except Exception as e:
        logging.error(f"Error in get_vendor_products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vendors", status_code=status.HTTP_201_CREATED)
def create_vendor(payload: Vendor):
    try:
        sql = "INSERT INTO tbl_vendor (vendorName, contactName, phone, email, address) VALUES (%s, %s, %s, %s, %s)"
        vendor_id = execute_sql(sql, (
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

@app.put("/vendors/{id}")
def update_vendor(id: int, payload: Vendor):
    try:
        sql = "UPDATE tbl_vendor SET vendorName=%s, contactName=%s, phone=%s, email=%s, address=%s WHERE vendorID=%s"
        execute_sql(sql, (
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

@app.delete("/vendors/{id}")
def delete_vendor(id: int):
    try:
        # Kiểm tra xem vendor có đang được sử dụng không
        usage = check_vendor_usage(id)
        
        if not usage['can_delete']:
            raise HTTPException(
                status_code=400, 
                detail=f"Không thể xóa nhà cung cấp này vì đang được sử dụng trong {usage['supplies_count']} bản ghi cung cấp sản phẩm"
            )
        
        execute_sql("DELETE FROM tbl_vendor WHERE vendorID = %s", (id,))
        return {"message": "Vendor deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in delete_vendor: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# ===== INVENTORY =====
@app.get("/inventories")
def get_inventory():
    try:
        # Lấy inventory kèm thông tin product từ stores
        query = """
            SELECT 
                i.*,
                s.productID,
                p.productName,
                p.productLine,
                p.productBrand
            FROM tbl_inventory i
            LEFT JOIN (
                SELECT DISTINCT inventoryID, productID 
                FROM tbl_stores 
                WHERE productID IS NOT NULL
            ) s ON i.inventoryID = s.inventoryID
            LEFT JOIN tbl_product p ON s.productID = p.productID
            ORDER BY i.inventoryID
        """
        return fetchall_sql(query)
    except Exception as e:
        logging.error(f"Error in get_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/inventories", status_code=status.HTTP_201_CREATED)
def create_inventory(payload: dict):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Tạo inventory record
            sql = """
                INSERT INTO tbl_inventory 
                (inventoryID, warehouse, maxStockLevel, stockQuantity, unitCost, lastedUpdate, inventoryNote, inventoryStatus) 
                VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s)
            """
            inventory_id = payload.get("inventoryID")
            cursor.execute(sql, (
                inventory_id,
                payload.get("warehouse"),
                payload.get("maxStockLevel"),
                payload.get("stockQuantity"),
                payload.get("unitCost"),
                payload.get("inventoryNote"),
                payload.get("inventoryStatus")
            ))
            
            # Nếu có productID, tạo relationship trong tbl_stores
            product_id = payload.get("productID")
            if product_id:
                # Kiểm tra product có tồn tại không
                cursor.execute("SELECT productID FROM tbl_product WHERE productID = %s", (product_id,))
                if not cursor.fetchone():
                    raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
                
                # Tạo stores relationship
                store_sql = """
                    INSERT INTO tbl_stores (productID, inventoryID, storeDate, quantityStore, roleStore)
                    VALUES (%s, %s, NOW(), %s, 'Initial')
                """
                cursor.execute(store_sql, (
                    product_id,
                    inventory_id,
                    payload.get("stockQuantity", 0)
                ))
            
            conn.commit()
        return {"message": "Inventory record created", "inventoryID": inventory_id}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in create_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)

@app.put("/inventories/{id}")
def update_inventory(id: int, payload: Inventory):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Cập nhật inventory record
            sql = """
                UPDATE tbl_inventory 
                SET warehouse=%s, maxStockLevel=%s, stockQuantity=%s, unitCost=%s, 
                    lastedUpdate=NOW(), inventoryNote=%s, inventoryStatus=%s 
                WHERE inventoryID=%s
            """
            cursor.execute(sql, (
                payload.warehouse,
                payload.maxStockLevel,
                payload.stockQuantity,
                payload.unitCost,
                payload.inventoryNote,
                payload.inventoryStatus,
                id
            ))
            
            # Nếu có productID, cập nhật hoặc tạo stores relationship
            if payload.productID:
                # Kiểm tra product có tồn tại không
                cursor.execute("SELECT productID FROM tbl_product WHERE productID = %s", (payload.productID,))
                if not cursor.fetchone():
                    raise HTTPException(status_code=404, detail=f"Product with ID {payload.productID} not found")
                
                # Kiểm tra xem stores relationship đã tồn tại chưa
                cursor.execute("""
                    SELECT storeID FROM tbl_stores 
                    WHERE inventoryID = %s AND productID = %s
                """, (id, payload.productID))
                existing_store = cursor.fetchone()
                
                if existing_store:
                    # Cập nhật stores relationship
                    cursor.execute("""
                        UPDATE tbl_stores 
                        SET quantityStore = %s, storeDate = NOW()
                        WHERE inventoryID = %s AND productID = %s
                    """, (payload.stockQuantity, id, payload.productID))
                else:
                    # Tạo stores relationship mới
                    cursor.execute("""
                        INSERT INTO tbl_stores (productID, inventoryID, storeDate, quantityStore, roleStore)
                        VALUES (%s, %s, NOW(), %s, 'Update')
                    """, (payload.productID, id, payload.stockQuantity))
            
            conn.commit()
        return {"message": "Inventory updated successfully"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in update_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)

@app.delete("/inventories/{id}")
def delete_inventory(id: int):
    try:
        # Kiểm tra xem inventory có đang được sử dụng không
        usage = check_inventory_usage(id)
        
        if not usage['can_delete']:
            raise HTTPException(
                status_code=400, 
                detail=f"Không thể xóa kho này vì đang được sử dụng trong {usage['stores_count']} bản ghi lưu trữ sản phẩm"
            )
        
        execute_sql("DELETE FROM tbl_inventory WHERE inventoryID = %s", (id,))
        return {"message": "Inventory record deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in delete_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===  REQUEST =====
@app.get("/requests")
def get_requests():
    try:
        return fetchall_sql("SELECT * FROM tbl_requests")
    except Exception as e:
        logging.error(f"Error in get_request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/requests/{id}")
def get_request(id: int):
    try:
        return fetchall_sql("SELECT * FROM tbl_requests join tbl_product on tbl_requests.productID = tbl_product.productID WHERE orderID = %s", (id,))
    except Exception as e:
        logging.error(f"Error in get_request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/requests", status_code=status.HTTP_201_CREATED)
def create_request(payload: Request):
    try:
        sql = "INSERT INTO tbl_requests (orderID, productID, quantityOrdered, discount, note) VALUES (%s, %s, %s, %s, %s)"
        request_id = execute_sql(sql, (
            payload.orderID, payload.productID, payload.quantityOrdered, payload.discount, payload.note
        ))
        return {"message": "Request created", "requestID": request_id}
    except Exception as e:
        logging.error(f"Error in create_request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/requests/{id}")
def update_request(id: int, payload: Request):
    try:
        sql = "UPDATE tbl_requests SET orderID=%s, productID=%s, quantityOrdered=%s, discount=%s, note=%s WHERE requestID=%s"
        execute_sql(sql, (
            payload.orderID, payload.productID, payload.quantityOrdered, payload.discount, payload.note, id
        ))
        return {"message": "Request updated successfully"}
    except Exception as e:
        logging.error(f"Error in update_request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/requests/{id}")
def delete_request(id: int):
    try:
        execute_sql("DELETE FROM tbl_requests WHERE requestID = %s", (id,))
        return {"message": "Request deleted"}
    except Exception as e:
        logging.error(f"Error in delete_request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===  STORE (Product-Inventory Relationship) =====
@app.get("/stores")
def get_store():
    try:
        # Lấy stores kèm thông tin product và inventory
        query = """
            SELECT 
                s.*,
                p.productName,
                p.productLine,
                p.productBrand,
                i.warehouse,
                i.stockQuantity as inventoryStock
            FROM tbl_stores s
            LEFT JOIN tbl_product p ON s.productID = p.productID
            LEFT JOIN tbl_inventory i ON s.inventoryID = i.inventoryID
            ORDER BY s.storeDate DESC
        """
        return fetchall_sql(query)
    except Exception as e:
        logging.error(f"Error in get_store: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stores/product/{product_id}")
def get_stores_by_product(product_id: int):
    """Lấy tất cả stores của một product"""
    try:
        query = """
            SELECT 
                s.*,
                i.warehouse,
                i.stockQuantity as inventoryStock
            FROM tbl_stores s
            LEFT JOIN tbl_inventory i ON s.inventoryID = i.inventoryID
            WHERE s.productID = %s
            ORDER BY s.storeDate DESC
        """
        return fetchall_sql(query, (product_id,))
    except Exception as e:
        logging.error(f"Error in get_stores_by_product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stores/inventory/{inventory_id}")
def get_stores_by_inventory(inventory_id: int):
    """Lấy tất cả stores của một inventory"""
    try:
        query = """
            SELECT 
                s.*,
                p.productName,
                p.productLine,
                p.productBrand
            FROM tbl_stores s
            LEFT JOIN tbl_product p ON s.productID = p.productID
            WHERE s.inventoryID = %s
            ORDER BY s.storeDate DESC
        """
        return fetchall_sql(query, (inventory_id,))
    except Exception as e:
        logging.error(f"Error in get_stores_by_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stores", status_code=status.HTTP_201_CREATED)
def create_store(payload: Store):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Kiểm tra product và inventory có tồn tại không
            cursor.execute("SELECT productID FROM tbl_product WHERE productID = %s", (payload.productID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Product with ID {payload.productID} not found")
            
            cursor.execute("SELECT inventoryID FROM tbl_inventory WHERE inventoryID = %s", (payload.inventoryID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Inventory with ID {payload.inventoryID} not found")
            
            # Tạo stores relationship
            sql = """
                INSERT INTO tbl_stores (productID, inventoryID, storeDate, quantityStore, roleStore) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                payload.productID, 
                payload.inventoryID, 
                payload.storeDate or datetime.datetime.now(), 
                payload.quantityStore, 
                payload.roleStore or 'Manual'
            ))
            
            # Cập nhật stock quantity trong inventory nếu roleStore là Import
            if payload.roleStore == 'Import':
                cursor.execute("""
                    UPDATE tbl_inventory 
                    SET stockQuantity = stockQuantity + %s, lastedUpdate = NOW()
                    WHERE inventoryID = %s
                """, (payload.quantityStore, payload.inventoryID))
            
            conn.commit()
            store_id = cursor.lastrowid
        return {"message": "Store created", "storeID": store_id}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in create_store: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)

@app.put("/stores/{id}")
def update_store(id: int, payload: Store):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Kiểm tra product và inventory có tồn tại không
            cursor.execute("SELECT productID FROM tbl_product WHERE productID = %s", (payload.productID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Product with ID {payload.productID} not found")
            
            cursor.execute("SELECT inventoryID FROM tbl_inventory WHERE inventoryID = %s", (payload.inventoryID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Inventory with ID {payload.inventoryID} not found")
            
            # Lấy số lượng cũ để tính toán chênh lệch
            cursor.execute("SELECT quantityStore, roleStore FROM tbl_stores WHERE storeID = %s", (id,))
            old_store = cursor.fetchone()
            if not old_store:
                raise HTTPException(status_code=404, detail="Store not found")
            
            old_quantity = old_store['quantityStore']
            quantity_diff = payload.quantityStore - old_quantity
            
            # Cập nhật stores relationship
            sql = """
                UPDATE tbl_stores 
                SET productID=%s, inventoryID=%s, storeDate=%s, quantityStore=%s, roleStore=%s 
                WHERE storeID=%s
            """
            cursor.execute(sql, (
                payload.productID, 
                payload.inventoryID, 
                payload.storeDate or datetime.datetime.now(), 
                payload.quantityStore, 
                payload.roleStore or 'Manual', 
                id
            ))
            
            # Cập nhật stock quantity trong inventory nếu có thay đổi
            if quantity_diff != 0 and payload.roleStore in ['Import', 'Manual']:
                cursor.execute("""
                    UPDATE tbl_inventory 
                    SET stockQuantity = stockQuantity + %s, lastedUpdate = NOW()
                    WHERE inventoryID = %s
                """, (quantity_diff, payload.inventoryID))
            
            conn.commit()
        return {"message": "Store updated successfully"}
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in update_store: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)
    
@app.delete("/stores/{id}")
def delete_store(id: int):
    try:
        execute_sql("DELETE FROM tbl_stores WHERE storeID = %s", (id,))
        return {"message": "Store deleted"}
    except Exception as e:
        logging.error(f"Error in delete_store: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# ===  SUPPLY (Product-Vendor Relationship) =====
@app.get("/supplies")
def get_supply():
    try:
        # Lấy supplies kèm thông tin product và vendor
        query = """
            SELECT 
                s.*,
                p.productName,
                p.productLine,
                p.productBrand,
                v.vendorName,
                v.contactName,
                v.phone
            FROM tbl_supplies s
            LEFT JOIN tbl_product p ON s.productID = p.productID
            LEFT JOIN tbl_vendor v ON s.vendorID = v.vendorID
            ORDER BY s.supplyDate DESC
        """
        return fetchall_sql(query)
    except Exception as e:
        logging.error(f"Error in get_supply: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/supplies/product/{product_id}")
def get_supplies_by_product(product_id: int):
    """Lấy tất cả supplies của một product"""
    try:
        query = """
            SELECT 
                s.*,
                v.vendorName,
                v.contactName,
                v.phone
            FROM tbl_supplies s
            LEFT JOIN tbl_vendor v ON s.vendorID = v.vendorID
            WHERE s.productID = %s
            ORDER BY s.supplyDate DESC
        """
        return fetchall_sql(query, (product_id,))
    except Exception as e:
        logging.error(f"Error in get_supplies_by_product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/supplies/vendor/{vendor_id}")
def get_supplies_by_vendor(vendor_id: int):
    """Lấy tất cả supplies của một vendor"""
    try:
        query = """
            SELECT 
                s.*,
                p.productName,
                p.productLine,
                p.productBrand
            FROM tbl_supplies s
            LEFT JOIN tbl_product p ON s.productID = p.productID
            WHERE s.vendorID = %s
            ORDER BY s.supplyDate DESC
        """
        return fetchall_sql(query, (vendor_id,))
    except Exception as e:
        logging.error(f"Error in get_supplies_by_vendor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/supplies", status_code=status.HTTP_201_CREATED)
def create_supply(payload: Supply):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Kiểm tra product và vendor có tồn tại không
            cursor.execute("SELECT productID FROM tbl_product WHERE productID = %s", (payload.productID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Product with ID {payload.productID} not found")
            
            cursor.execute("SELECT vendorID FROM tbl_vendor WHERE vendorID = %s", (payload.vendorID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Vendor with ID {payload.vendorID} not found")
            
            # Tạo supplies relationship
            sql = """
                INSERT INTO tbl_supplies (productID, vendorID, supplyDate, quantitySupplier, note) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                payload.productID, 
                payload.vendorID, 
                payload.supplyDate or datetime.datetime.now(), 
                payload.quantitySupplier, 
                payload.note
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
    
@app.put("/supplies/{id}")
def update_supply(id: int, payload: Supply):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Kiểm tra product và vendor có tồn tại không
            cursor.execute("SELECT productID FROM tbl_product WHERE productID = %s", (payload.productID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Product with ID {payload.productID} not found")
            
            cursor.execute("SELECT vendorID FROM tbl_vendor WHERE vendorID = %s", (payload.vendorID,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Vendor with ID {payload.vendorID} not found")
            
            # Cập nhật supplies relationship
            sql = """
                UPDATE tbl_supplies 
                SET productID=%s, vendorID=%s, supplyDate=%s, quantitySupplier=%s, note=%s 
                WHERE supplyID=%s
            """
            cursor.execute(sql, (
                payload.productID, 
                payload.vendorID, 
                payload.supplyDate or datetime.datetime.now(), 
                payload.quantitySupplier, 
                payload.note, 
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
@app.delete("/supplies/{id}")
def delete_supply(id: int):
    try:
        execute_sql("DELETE FROM tbl_supplies WHERE supplyID = %s", (id,))
        return {"message": "Supply deleted"}
    except Exception as e:
        logging.error(f"Error in delete_supply: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== PRODUCT CATEGORIES =====
@app.get("/categories")
def get_categories():
    try:
        # Lấy danh sách categories từ productLine (hoặc tạo bảng riêng nếu cần)
        return fetchall_sql("SELECT DISTINCT productLine as categoryName FROM tbl_product WHERE productLine IS NOT NULL")
    except Exception as e:
        logging.error(f"Error in get_categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories/products")
def get_products_by_category():
    try:
        # Đếm số sản phẩm theo từng category
        return fetchall_sql("""
            SELECT productLine as categoryName, COUNT(*) as productCount 
            FROM tbl_product 
            WHERE productLine IS NOT NULL 
            GROUP BY productLine
        """)
    except Exception as e:
        logging.error(f"Error in get_products_by_category: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== CUSTOMER DEBTS =====
@app.get("/customers/{id}/debts")
def get_customer_debts(id: int):
    try:
        # Tính công nợ dựa trên orders chưa thanh toán
        query = """
            SELECT 
                o.orderID,
                o.totalAmount,
                o.orderDate,
                COALESCE(SUM(p.transactionAmount), 0) as paidAmount,
                (o.totalAmount - COALESCE(SUM(p.transactionAmount), 0)) as debtAmount
            FROM tbl_order o
            LEFT JOIN tbl_payment p ON o.orderID = p.orderID
            WHERE o.customerID = %s AND o.paymentStatus != 'Paid'
            GROUP BY o.orderID, o.totalAmount, o.orderDate
            HAVING debtAmount > 0
        """
        return fetchall_sql(query, (id,))
    except Exception as e:
        logging.error(f"Error in get_customer_debts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debts")
def get_all_debts():
    try:
        # Lấy tất cả công nợ của khách hàng
        query = """
            SELECT 
                c.customerID,
                c.customerName,
                c.phone,
                SUM(o.totalAmount - COALESCE(p.paidAmount, 0)) as totalDebt
            FROM tbl_customer c
            INNER JOIN tbl_order o ON c.customerID = o.customerID
            LEFT JOIN (
                SELECT orderID, SUM(transactionAmount) as paidAmount
                FROM tbl_payment
                GROUP BY orderID
            ) p ON o.orderID = p.orderID
            WHERE o.paymentStatus != 'Paid'
            GROUP BY c.customerID, c.customerName, c.phone
            HAVING totalDebt > 0
        """
        return fetchall_sql(query)
    except Exception as e:
        logging.error(f"Error in get_all_debts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== INVENTORY OPERATIONS =====
@app.post("/inventory/import", status_code=status.HTTP_201_CREATED)
def import_inventory(payload: InventoryImport):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Thêm vào stores (lịch sử nhập kho)
            cursor.execute("""
                INSERT INTO tbl_stores (productID, inventoryID, storeDate, quantityStore, roleStore)
                VALUES (%s, %s, %s, %s, 'Import')
            """, (payload.productID, payload.inventoryID, payload.importDate or datetime.datetime.now(), payload.quantity))
            
            # Kiểm tra xem inventory record đã tồn tại chưa
            cursor.execute("""
                SELECT inventoryID FROM tbl_inventory 
                WHERE inventoryID = %s
            """, (payload.inventoryID,))
            inv_exists = cursor.fetchone()
            
            if inv_exists:
                # Cập nhật stock quantity nếu inventory đã tồn tại
                cursor.execute("""
                    UPDATE tbl_inventory 
                    SET stockQuantity = stockQuantity + %s, 
                        unitCost = %s,
                        lastedUpdate = NOW()
                    WHERE inventoryID = %s
                """, (payload.quantity, payload.unitCost, payload.inventoryID))
            else:
                # Tạo inventory record mới nếu chưa có
                cursor.execute("""
                    INSERT INTO tbl_inventory (inventoryID, warehouse, stockQuantity, unitCost, lastedUpdate, inventoryStatus)
                    VALUES (%s, 'Main Warehouse', %s, %s, NOW(), 'Active')
                """, (payload.inventoryID, payload.quantity, payload.unitCost))
            
            conn.commit()
        return {"message": "Inventory imported successfully"}
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error in import_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        safe_close_connection(conn)

@app.post("/inventory/export", status_code=status.HTTP_201_CREATED)
def export_inventory(payload: InventoryExport):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Kiểm tra số lượng tồn kho
            cursor.execute("""
                SELECT stockQuantity FROM tbl_inventory 
                WHERE inventoryID = %s
            """, (payload.inventoryID,))
            result = cursor.fetchone()
            if not result or result['stockQuantity'] < payload.quantity:
                raise HTTPException(status_code=400, detail="Insufficient inventory")
            
            # Thêm vào stores với roleStore = 'Export' (số lượng âm)
            cursor.execute("""
                INSERT INTO tbl_stores (productID, inventoryID, storeDate, quantityStore, roleStore)
                VALUES (%s, %s, %s, %s, 'Export')
            """, (payload.productID, payload.inventoryID, payload.exportDate or datetime.datetime.now(), -payload.quantity))
            
            # Cập nhật stock quantity
            cursor.execute("""
                UPDATE tbl_inventory 
                SET stockQuantity = stockQuantity - %s,
                    lastedUpdate = NOW()
                WHERE inventoryID = %s
            """, (payload.quantity, payload.inventoryID))
            
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

@app.post("/inventory/stocktaking", status_code=status.HTTP_201_CREATED)
def stocktaking(payload: Stocktaking):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Lấy số lượng hiện tại
            cursor.execute("""
                SELECT stockQuantity FROM tbl_inventory 
                WHERE inventoryID = %s
            """, (payload.inventoryID,))
            current = cursor.fetchone()
            if not current:
                raise HTTPException(status_code=404, detail="Inventory not found")
            
            difference = payload.actualQuantity - current['stockQuantity']
            
            # Cập nhật số lượng thực tế
            cursor.execute("""
                UPDATE tbl_inventory 
                SET stockQuantity = %s,
                    lastedUpdate = NOW()
                WHERE inventoryID = %s
            """, (payload.actualQuantity, payload.inventoryID))
            
            # Ghi lại lịch sử kiểm kê vào stores
            if difference != 0:
                cursor.execute("""
                    INSERT INTO tbl_stores (productID, inventoryID, storeDate, quantityStore, roleStore)
                    VALUES (%s, %s, %s, %s, 'Stocktaking')
                """, (payload.productID, payload.inventoryID, payload.stocktakingDate or datetime.datetime.now(), difference))
            
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


# ===== REPORTS =====
@app.get("/reports/revenue")
def get_revenue_report(start_date: Optional[str] = None, end_date: Optional[str] = None):
    try:
        conditions = []
        params = []
        if start_date:
            conditions.append("o.orderDate >= %s")
            params.append(start_date)
        if end_date:
            conditions.append("o.orderDate <= %s")
            params.append(end_date)
        
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"""
            SELECT 
                DATE(o.orderDate) as date,
                COUNT(DISTINCT o.orderID) as orderCount,
                SUM(o.totalAmount) as totalRevenue,
                SUM(CASE WHEN o.paymentStatus = 'Paid' THEN o.totalAmount ELSE 0 END) as paidAmount,
                SUM(CASE WHEN o.paymentStatus != 'Paid' THEN o.totalAmount ELSE 0 END) as unpaidAmount
            FROM tbl_order o
            {where_clause}
            GROUP BY DATE(o.orderDate)
            ORDER BY date DESC
        """
        return fetchall_sql(query, tuple(params) if params else ())
    except Exception as e:
        logging.error(f"Error in get_revenue_report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/top-products")
def get_top_products(limit: int = 10, start_date: Optional[str] = None, end_date: Optional[str] = None):
    try:
        conditions = []
        params = []
        if start_date:
            conditions.append("o.orderDate >= %s")
            params.append(start_date)
        if end_date:
            conditions.append("o.orderDate <= %s")
            params.append(end_date)
        
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        params_list = list(params)
        params_list.append(limit)
        
        query = f"""
            SELECT 
                p.productID,
                p.productName,
                p.productLine,
                p.productBrand,
                SUM(r.quantityOrdered) as totalQuantitySold,
                SUM(r.quantityOrdered * p.priceEach) as totalRevenue
            FROM tbl_product p
            INNER JOIN tbl_requests r ON p.productID = r.productID
            INNER JOIN tbl_order o ON r.orderID = o.orderID
            {where_clause}
            GROUP BY p.productID, p.productName, p.productLine, p.productBrand
            ORDER BY totalQuantitySold DESC
            LIMIT %s
        """
        return fetchall_sql(query, tuple(params_list))
    except Exception as e:
        logging.error(f"Error in get_top_products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/inventory")
def get_inventory_report():
    try:
        # Lấy thông tin inventory kết hợp với stores để lấy productID
        query = """
            SELECT 
                i.inventoryID,
                i.warehouse,
                s.productID,
                p.productName,
                i.stockQuantity,
                i.maxStockLevel,
                i.unitCost,
                (i.stockQuantity * i.unitCost) as totalValue,
                CASE 
                    WHEN i.stockQuantity = 0 THEN 'Out of Stock'
                    WHEN i.maxStockLevel > 0 AND i.stockQuantity < i.maxStockLevel * 0.2 THEN 'Low Stock'
                    ELSE 'In Stock'
                END as status
            FROM tbl_inventory i
            LEFT JOIN (
                SELECT DISTINCT inventoryID, productID 
                FROM tbl_stores 
                WHERE productID IS NOT NULL
            ) s ON i.inventoryID = s.inventoryID
            LEFT JOIN tbl_product p ON s.productID = p.productID
            ORDER BY i.warehouse, p.productName
        """
        return fetchall_sql(query)
    except Exception as e:
        logging.error(f"Error in get_inventory_report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/summary")
def get_summary_report():
    try:
        # Tổng hợp các thống kê chính
        summary = {}
        
        # Tổng số khách hàng
        summary['totalCustomers'] = fetchall_sql("SELECT COUNT(*) as count FROM tbl_customer")[0]['count']
        
        # Tổng số sản phẩm
        summary['totalProducts'] = fetchall_sql("SELECT COUNT(*) as count FROM tbl_product")[0]['count']
        
        # Tổng số đơn hàng
        summary['totalOrders'] = fetchall_sql("SELECT COUNT(*) as count FROM tbl_order")[0]['count']
        
        # Tổng doanh thu
        revenue = fetchall_sql("SELECT SUM(totalAmount) as total FROM tbl_order WHERE paymentStatus = 'Paid'")
        summary['totalRevenue'] = revenue[0]['total'] or 0
        
        # Tổng công nợ
        debts = fetchall_sql("""
            SELECT SUM(o.totalAmount - COALESCE(p.paidAmount, 0)) as total
            FROM tbl_order o
            LEFT JOIN (
                SELECT orderID, SUM(transactionAmount) as paidAmount
                FROM tbl_payment
                GROUP BY orderID
            ) p ON o.orderID = p.orderID
            WHERE o.paymentStatus != 'Paid'
        """)
        summary['totalDebts'] = debts[0]['total'] or 0
        
        # Tổng giá trị tồn kho
        inventory = fetchall_sql("SELECT SUM(stockQuantity * unitCost) as total FROM tbl_inventory")
        summary['totalInventoryValue'] = inventory[0]['total'] or 0
        
        return summary
    except Exception as e:
        logging.error(f"Error in get_summary_report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== AUTH: REGISTER & LOGIN =====

# public customer registration
@app.post("/register/customer", status_code=status.HTTP_201_CREATED)
def register_customer(payload: RegisterCustomerModel):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM tbl_customer WHERE phone=%s OR email=%s", (payload.phone, payload.email))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Phone or email already exists")

            password_hash = generate_password_hash(payload.password)
            sql = """
                INSERT INTO tbl_customer (
                    customerName, phone, email, address, postalCode,
                    customerType, loyalPoint, loyalLevel, passwordHash
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            cursor.execute(sql, (
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
@app.post("/register/staff", status_code=status.HTTP_201_CREATED)
def register_staff(payload: RegisterStaffModel):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM tbl_staff WHERE phone=%s OR email=%s", (payload.phone, payload.email))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Staff phone or email already exists")

            password_hash = generate_password_hash(payload.password)
            sql = """
                INSERT INTO tbl_staff (
                    staffName, position, phone, email, address, managerID, salary, passwordHash
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """
            cursor.execute(sql, (
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


@app.post("/login/customer")
def login_customer(payload: LoginModel):
    conn = None
    try:
        identifier = payload.identifier
        password = payload.password
        if not identifier or not password:
            raise HTTPException(status_code=400, detail="Missing identifier or password")

        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tbl_customer WHERE email=%s OR phone=%s", (identifier, identifier))
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
        
@app.post("/login/staff")
def login_staff(payload: LoginModel):
    conn = None
    try:
        identifier = payload.identifier
        password = payload.password
        if not identifier or not password:
            raise HTTPException(status_code=400, detail="Missing identifier or password")

        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tbl_staff WHERE email=%s OR phone=%s", (identifier, identifier))
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
    

# ===== ERROR HANDLING =====
@app.exception_handler(404)
def not_found_handler(request, exc):
    return ORJSONResponse(status_code=404, content={"error": "Resource not found"})

@app.exception_handler(500)
def internal_error_handler(request, exc):
    return ORJSONResponse(status_code=500, content={"error": "Internal server error"})

# ===== MAIN =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host=SERVER_HOST, port=SERVER_PORT, reload=SERVER_RELOAD)