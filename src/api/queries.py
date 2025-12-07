"""
This file contains all the SQL queries used in the application.
"""

# ===== CHECK USAGE =====
CHECK_PRODUCT_IN_REQUESTS = "SELECT COUNT(*) as count FROM tbl_requests WHERE productID = %s"
CHECK_PRODUCT_IN_STORES = "SELECT COUNT(*) as count FROM tbl_stores WHERE productID = %s"
CHECK_PRODUCT_IN_SUPPLIES = "SELECT COUNT(*) as count FROM tbl_supplies WHERE productID = %s"
CHECK_VENDOR_IN_SUPPLIES = "SELECT COUNT(*) as count FROM tbl_supplies WHERE vendorID = %s"
CHECK_INVENTORY_IN_STORES = "SELECT COUNT(*) as count FROM tbl_stores WHERE inventoryID = %s"

# ===== CUSTOMERS =====
SELECT_CUSTOMERS = "SELECT customerID, customerName, phone, email, address, postalCode, customerType, loyalPoint, loyalLevel FROM tbl_customer"
SELECT_CUSTOMERS_SEARCH = """
    SELECT customerID, customerName, phone, email, address, postalCode, customerType, loyalPoint, loyalLevel 
    FROM tbl_customer 
    WHERE customerName LIKE %s OR phone LIKE %s OR email LIKE %s
"""
SELECT_CUSTOMER_BY_ID = "SELECT customerID, customerName, phone, email, address, postalCode, customerType, loyalPoint, loyalLevel FROM tbl_customer WHERE customerID = %s"
INSERT_CUSTOMER = "INSERT INTO tbl_customer (customerName, phone, email, address, postalCode) VALUES (%s, %s, %s, %s, %s)"
UPDATE_CUSTOMER = "UPDATE tbl_customer SET customerName=%s, phone=%s, email=%s, address=%s, postalCode=%s WHERE customerID=%s"
DELETE_CUSTOMER = "DELETE FROM tbl_customer WHERE customerID = %s"

# ===== PRODUCTS =====
SELECT_PRODUCTS = "SELECT * FROM tbl_product"
SELECT_PRODUCT_BY_ID = "SELECT * FROM tbl_product WHERE productID = %s"
SELECT_PRODUCT_INVENTORY = """
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
SELECT_PRODUCT_SUPPLIERS = """
    SELECT
        v.*,
        s.supplyDate,
        s.quantitySupplier
    FROM tbl_vendor v
    INNER JOIN tbl_supplies s ON v.vendorID = s.vendorID
    WHERE s.productID = %s
    ORDER BY s.supplyDate DESC
    """
INSERT_PRODUCT = """
    INSERT INTO tbl_product (
        productName, priceEach, productLine, productScale,
        productBrand, productDiscription, warrantyPeriod, MSRP
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""
UPDATE_PRODUCT = """
    UPDATE tbl_product
    SET productName=%s, priceEach=%s, productLine=%s, productScale=%s,
        productBrand=%s, productDiscription=%s, warrantyPeriod=%s, MSRP=%s
    WHERE productID=%s
"""
DELETE_PRODUCT = "DELETE FROM tbl_product WHERE productID = %s"

# ===== ORDERS =====
SELECT_ORDER_BY_CUSTOMER_ID = "SELECT * FROM tbl_order WHERE customerID = %s"
INSERT_ORDER = """
    INSERT INTO tbl_order (
        totalAmount, orderStatus,  paymentStatus,
        pickupMethod, shippedDate, shippedStatus, customerID, staffID
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
UPDATE_ORDER = """
    UPDATE tbl_order
    SET orderStatus=%s, paymentStatus=%s, pickupMethod=%s,
        shippedStatus=%s, shippedDate=%s, totalAmount=%s
    WHERE orderID=%s
"""
DELETE_ORDER = "DELETE FROM tbl_order WHERE orderID = %s"
CHECKOUT_INSERT_ORDER = """
    INSERT INTO tbl_order (
        totalAmount, orderStatus, paymentStatus,
        pickupMethod, shippedDate, shippedStatus, customerID, staffID
    ) VALUES (%s,'Pending',%s,%s,%s,%s,%s,%s,%s)
"""
CHECKOUT_INSERT_REQUEST = """
    INSERT INTO tbl_requests (orderID, productID, quantityOrdered, discount, note)
    VALUES (%s,%s,%s,%s,%s)
"""
CHECKOUT_INSERT_PAYMENT = """
    INSERT INTO tbl_payment (orderID, transactionAmount, paymentMethod, transactionDate, transactionStatus)
    VALUES (%s,%s,%s,NOW(),'Pending')
"""

# ===== PAYMENTS =====
SELECT_PAYMENTS = "SELECT * FROM tbl_payment"
INSERT_PAYMENT = """
    INSERT INTO tbl_payment (orderID, transactionAmount, paymentMethod, transactionDate, transactionStatus)
    VALUES (%s, %s, %s, NOW(), %s)
"""
UPDATE_PAYMENT = """
    UPDATE tbl_payment
    SET orderID=%s, transactionAmount=%s, paymentMethod=%s, transactionDate=NOW(), transactionStatus=%s
    WHERE paymentID=%s
"""
DELETE_PAYMENT = "DELETE FROM tbl_payment WHERE paymentID = %s"

# ===== STAFF =====
SELECT_STAFFS = "SELECT staffID, staffName, position, phone, email, address, managerID, salary FROM tbl_staff"
INSERT_STAFF = """
    INSERT INTO tbl_staff (staffName, position, phone, email, address, managerID, salary)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""
UPDATE_STAFF = """
    UPDATE tbl_staff SET staffName=%s, position=%s, phone=%s, email=%s, address=%s, managerID=%s, salary=%s WHERE staffID=%s
"""
DELETE_STAFF = "DELETE FROM tbl_staff WHERE staffID = %s"

# ===== VENDORS =====
SELECT_VENDORS = """
    SELECT 
        v.*,
        COUNT(DISTINCT s.productID) as productCount
    FROM tbl_vendor v
    LEFT JOIN tbl_supplies s ON v.vendorID = s.vendorID
    GROUP BY v.vendorID
    ORDER BY v.vendorID
"""

INSERT_VENDOR = "INSERT INTO tbl_vendor (vendorName, contactName, phone, email, address) VALUES (%s, %s, %s, %s, %s)"
UPDATE_VENDOR = "UPDATE tbl_vendor SET vendorName=%s, contactName=%s, phone=%s, address=%s WHERE vendorID=%s"
DELETE_VENDOR = "DELETE FROM tbl_vendor WHERE vendorID = %s"

# ===== INVENTORY =====
SELECT_INVENTORIES = """
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
INSERT_INVENTORY = """
    INSERT INTO tbl_inventory 
    (inventoryID, warehouse, maxStockLevel, stockQuantity, unitCost, lastedUpdate, inventoryNote, inventoryStatus) 
    VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s)
"""
SELECT_PRODUCT_BY_ID_FOR_INVENTORY = "SELECT productID FROM tbl_product WHERE productID = %s"
INSERT_STORE_FOR_INVENTORY = """
    INSERT INTO tbl_stores (productID, inventoryID, storeDate, quantityStore, roleStore)
    VALUES (%s, %s, NOW(), %s, 'Initial')
"""
UPDATE_INVENTORY = """
    UPDATE tbl_inventory 
    SET warehouse=%s, maxStockLevel=%s, stockQuantity=%s, unitCost=%s, 
        lastedUpdate=NOW(), inventoryNote=%s, inventoryStatus=%s 
    WHERE inventoryID=%s
"""
UPDATE_STORE_FOR_INVENTORY_UPDATE = """
    UPDATE tbl_stores 
    SET quantityStore = %s, storeDate = NOW()
    WHERE productID = %s
"""
INSERT_STORE_FOR_INVENTORY_UPDATE = """
    INSERT INTO tbl_stores (productID, inventoryID, storeDate, quantityStore, roleStore)
    VALUES (%s, %s, NOW(), %s, 'Update')
"""
DELETE_INVENTORY = "DELETE FROM tbl_inventory WHERE inventoryID = %s"

# ===== REQUESTS =====
SELECT_REQUESTS = "SELECT * FROM tbl_requests"
SELECT_PRODUCT_BY_ORDERID = "SELECT * FROM tbl_requests WHERE orderID = %s"
INSERT_REQUEST = "INSERT INTO tbl_requests (orderID, productID, quantityOrdered, discount, note) VALUES (%s, %s, %s, %s, %s)"
UPDATE_REQUEST = "UPDATE tbl_requests SET orderID=%s, productID=%s, quantityOrdered=%s, discount=%s, note=%s WHERE orderID=%s"
DELETE_REQUEST = "DELETE FROM tbl_requests WHERE requestID = %s"

# ===== STORES =====
SELECT_STORES = """
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
SELECT_STORES_BY_PRODUCT = """
    SELECT 
        s.*,
        i.warehouse,
        i.stockQuantity as inventoryStock
    FROM tbl_stores s
    LEFT JOIN tbl_inventory i ON s.inventoryID = i.inventoryID
    WHERE s.productID = %s
    ORDER BY s.storeDate DESC
"""
SELECT_STORES_BY_INVENTORY = """
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
SELECT_PRODUCT_FOR_STORE = "SELECT productID FROM tbl_product WHERE productID = %s"
SELECT_INVENTORY_FOR_STORE = "SELECT inventoryID FROM tbl_inventory WHERE inventoryID = %s"
INSERT_STORE = """
    INSERT INTO tbl_stores (productID, inventoryID, storeDate, quantityStore, roleStore) 
    VALUES (%s, %s, %s, %s, %s)
"""

SELECT_STORE = """
    SELECT quantityStore 
    FROM tbl_stores 
    WHERE productID = %s
"""

UPDATE_INVENTORY_FOR_STORE_IMPORT = """
    UPDATE tbl_inventory 
    SET stockQuantity = stockQuantity + %s, lastedUpdate = NOW()
    WHERE inventoryID = %s
"""
SELECT_STORE_BY_ID = "SELECT quantityStore, roleStore FROM tbl_stores WHERE productID = %s"
UPDATE_STORE = """
    UPDATE tbl_stores 
    SET productID=%s, storeDate=%s, quantityStore=%s, roleStore=%s 
    WHERE productID=%s
"""
UPDATE_INVENTORY_FOR_STORE_UPDATE = """
    UPDATE tbl_inventory 
    SET stockQuantity = stockQuantity + %s, lastedUpdate = NOW()
    WHERE inventoryID = %s
"""
DELETE_STORE = "DELETE FROM tbl_stores WHERE productID = %s"

# ===== SUPPLIES =====
SELECT_SUPPLIES = """
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
SELECT_SUPPLIES_BY_PRODUCT = """
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
SELECT_SUPPLIES_BY_VENDOR = """
    SELECT 
        *
    FROM tbl_supplies s
    WHERE s.vendorID = %s
    ORDER BY s.supplyDate DESC
"""
SELECT_PRODUCT_FOR_SUPPLY = "SELECT productID FROM tbl_product WHERE productID = %s"
SELECT_VENDOR_FOR_SUPPLY = "SELECT vendorID FROM tbl_vendor WHERE vendorID = %s"

INSERT_SUPPLY = """
    INSERT INTO tbl_supplies (productID, vendorID, supplyDate, quantitySupplier, handledBy) 
    VALUES (%s, %s, %s, %s, %s)
"""
UPDATE_SUPPLY = """
    UPDATE tbl_supplies 
    SET productID=%s, vendorID=%s, supplyDate=%s, quantitySupplier=%s, handledBy=%s 
    WHERE productID=%s
"""
DELETE_SUPPLY = "DELETE FROM tbl_supplies WHERE productID = %s"
SELECT_SUPPLY_BY_ID = "SELECT * FROM tbl_supplies WHERE productID = %s"

# ===== CATEGORIES =====
SELECT_CATEGORIES = "SELECT DISTINCT productLine as categoryName FROM tbl_product WHERE productLine IS NOT NULL"
SELECT_PRODUCTS_BY_CATEGORY = """
    SELECT productLine as categoryName, COUNT(*) as productCount 
    FROM tbl_product 
    WHERE productLine IS NOT NULL 
    GROUP BY productLine
"""

# ===== CUSTOMER DEBTS =====
SELECT_CUSTOMER_DEBTS = """
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
SELECT_ALL_DEBTS = """
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

# ===== INVENTORY OPERATIONS =====
INSERT_STORE_FOR_INVENTORY_IMPORT = """
    INSERT INTO tbl_stores (productID, inventoryID, storeDate, quantityStore, roleStore)
    VALUES (%s, %s, %s, %s, 'Import')
"""
SELECT_INVENTORY_BY_ID = "SELECT inventoryID FROM tbl_inventory WHERE inventoryID = %s"
UPDATE_INVENTORY_FOR_IMPORT = """
    UPDATE tbl_inventory 
    SET stockQuantity = stockQuantity + %s, 
        unitCost = %s,
        lastedUpdate = NOW()
    WHERE inventoryID = %s
"""
INSERT_INVENTORY_FOR_IMPORT = """
    INSERT INTO tbl_inventory (inventoryID, warehouse, stockQuantity, unitCost, lastedUpdate, inventoryStatus)
    VALUES (%s, 'Main Warehouse', %s, %s, NOW(), 'Active')
"""
SELECT_STOCK_QUANTITY_FOR_EXPORT = "SELECT stockQuantity FROM tbl_inventory WHERE inventoryID = %s"
INSERT_STORE_FOR_EXPORT = """
    INSERT INTO tbl_stores (productID, inventoryID, storeDate, quantityStore, roleStore)
    VALUES (%s, %s, %s, %s, 'Export')
"""
UPDATE_INVENTORY_FOR_EXPORT = """
    UPDATE tbl_inventory 
    SET stockQuantity = stockQuantity - %s,
        lastedUpdate = NOW()
    WHERE inventoryID = %s
"""
SELECT_STOCK_QUANTITY_FOR_STOCKTAKING = "SELECT stockQuantity FROM tbl_inventory WHERE inventoryID = %s"
UPDATE_INVENTORY_FOR_STOCKTAKING = """
    UPDATE tbl_inventory 
    SET stockQuantity = %s,
        lastedUpdate = NOW()
    WHERE inventoryID = %s
"""
INSERT_STORE_FOR_STOCKTAKING = """
    INSERT INTO tbl_stores (productID, inventoryID, storeDate, quantityStore, roleStore)
    VALUES (%s, %s, %s, %s, 'Stocktaking')
"""

# ===== REPORTS =====
SELECT_REVENUE_REPORT = """
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
SELECT_TOP_PRODUCTS_REPORT = """
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
SELECT_INVENTORY_REPORT = """
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
SUMMARY_TOTAL_CUSTOMERS = "SELECT COUNT(*) as count FROM tbl_customer"
SUMMARY_TOTAL_PRODUCTS = "SELECT COUNT(*) as count FROM tbl_product"
SUMMARY_TOTAL_ORDERS = "SELECT COUNT(*) as count FROM tbl_order"
SUMMARY_TOTAL_REVENUE = "SELECT SUM(totalAmount) as total FROM tbl_order WHERE paymentStatus = 'Paid'"
SUMMARY_TOTAL_DEBTS = """
    SELECT SUM(o.totalAmount - COALESCE(p.paidAmount, 0)) as total
    FROM tbl_order o
    LEFT JOIN (
        SELECT orderID, SUM(transactionAmount) as paidAmount
        FROM tbl_payment
        GROUP BY orderID
    ) p ON o.orderID = p.orderID
    WHERE o.paymentStatus != 'Paid'
"""
SUMMARY_TOTAL_INVENTORY_VALUE = "SELECT SUM(stockQuantity * unitCost) as total FROM tbl_inventory"

# ===== AUTH =====
SELECT_CUSTOMER_FOR_AUTH = "SELECT * FROM tbl_customer WHERE phone=%s OR email=%s"
INSERT_CUSTOMER_FOR_AUTH = """
    INSERT INTO tbl_customer (
        customerName, phone, email, address, postalCode,
        customerType, loyalPoint, loyalLevel, passwordHash
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""
SELECT_STAFF_FOR_AUTH = "SELECT * FROM tbl_staff WHERE phone=%s OR email=%s"
INSERT_STAFF_FOR_AUTH = """
    INSERT INTO tbl_staff (
        staffName, position, phone, email, address, managerID, salary, passwordHash
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
"""
LOGIN_CUSTOMER = "SELECT * FROM tbl_customer WHERE email=%s OR phone=%s"
LOGIN_STAFF = "SELECT * FROM tbl_staff WHERE email=%s OR phone=%s"
