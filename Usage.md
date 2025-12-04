# **Store Management System - Implementation Guide**

## **Project Overview**
Hệ thống quản lý cửa hàng bao gồm:
- **Backend API**: FastAPI (Python) - Xử lý logic nghiệp vụ và cơ sở dữ liệu
- **Customer Frontend**: React SPA cho khách hàng mua sắm
- **Manager Frontend**: React SPA cho quản lý cửa hàng

---

## **A. Backend API (FastAPI)**

### **1. Prerequisites (Yêu cầu hệ thống)**
- **Python**: 3.8+
- **MySQL Server**: 5.7+ hoặc MariaDB 10.0+
- **Git**: Để clone repository (tùy chọn)

### **2. Installation (Cài đặt)**

#### **Bước 1: Chuẩn bị môi trường Python**
```bash
# Kiểm tra phiên bản Python
python --version

# Tạo môi trường ảo (khuyến nghị)
python -m venv venv

# Kích hoạt môi trường ảo
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### **Bước 2: Cài đặt dependencies**
```bash
# Cài đặt các thư viện cần thiết
pip install fastapi uvicorn pymysql werkzeug python-multipart orjson

# Hoặc tạo file requirements.txt và cài đặt:
# echo "fastapi==0.104.1" > requirements.txt
# echo "uvicorn[standard]==0.24.0" >> requirements.txt
# echo "pymysql==1.1.0" >> requirements.txt
# echo "werkzeug==3.0.1" >> requirements.txt
# echo "orjson==3.9.10" >> requirements.txt
# pip install -r requirements.txt
```

#### **Bước 3: Cấu hình Database**
```sql
-- Tạo database (chạy trong MySQL)
CREATE DATABASE storemanagesystem CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tạo user (tùy chọn)
CREATE USER 'storeuser'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON storemanagesystem.* TO 'storeuser'@'localhost';
FLUSH PRIVILEGES;
```

#### **Bước 4: Cấu hình API**
Chỉnh sửa file `src/api/config.py`:
```python
# Database configuration
DB_CONFIG = {
    "host": "localhost",          # Địa chỉ MySQL server
    "user": "root",              # Username MySQL
    "password": "12345678",      # Password MySQL
    "db": "storemanagesystem",   # Tên database
}

# Server configuration
SERVER_HOST = "192.168.80.70"   # IP server (0.0.0.0 cho tất cả interfaces)
SERVER_PORT = 6868              # Port API
SERVER_RELOAD = True            # Auto-reload trong development

# CORS configuration
CORS_ALLOW_ORIGINS = ["*"]      # Cho phép tất cả origins (development)
```

### **3. Usage (Sử dụng)**

#### **Chạy API Server**
```bash
# Từ thư mục gốc của dự án
uvicorn src.api.main:app --host 192.168.80.70 --port 6868 --reload

# Hoặc sử dụng cấu hình từ config.py
python -m uvicorn src.api.main:app --reload
```

#### **Truy cập API Documentation**
- **Swagger UI**: `http://192.168.80.70:6868/docs`
- **ReDoc**: `http://192.168.80.70:6868/redoc`
- **OpenAPI JSON**: `http://192.168.80.70:6868/openapi.json`

#### **Test API Endpoints**
```bash
# Test health check
curl http://192.168.80.70:6868/docs

# Test products endpoint
curl http://192.168.80.70:6868/products
```

### **4. Component Roles & Functions (Vai trò các thành phần)**

#### **src/api/main.py - Application Entry Point**
- **Khởi tạo FastAPI app** với ORJSON response
- **Cấu hình CORS** cho cross-origin requests
- **Include tất cả routers** từ thư mục routers/
- **Xử lý lỗi toàn cục** (404, 500)
- **Chạy server** với uvicorn

#### **src/api/config.py - Configuration Management**
- **Server settings**: Host, port, reload mode
- **Database connection**: MySQL credentials
- **CORS policy**: Allowed origins, methods, headers
- **Logging level**: DEBUG, INFO, WARNING, ERROR

#### **src/api/db.py - Database Connection Layer**
- **get_connection()**: Tạo kết nối MySQL an toàn
- **safe_close_connection()**: Đóng kết nối proper
- **fetchall_sql()**: Thực thi SELECT queries, trả về list dict
- **execute_sql()**: Thực thi INSERT/UPDATE/DELETE, trả về lastrowid

#### **src/api/queries.py - SQL Query Repository**
- **Tập trung tất cả SQL queries** trong một file
- **Đặt tên constants** cho các câu query
- **Dễ maintain và refactor** SQL logic
- **Parameterized queries** để tránh SQL injection

#### **src/api/models/ - Data Models (Pydantic)**
- **Product.py**: Định nghĩa Product schema (name, price, category, etc.)
- **Order.py**: Order và OrderCheckoutModel schemas
- **Customer.py**: Customer và CustomerDebt schemas
- **Auth.py**: RegisterModel, LoginModel cho authentication
- **Inventory.py**: InventoryImport, InventoryExport, Stocktaking schemas

#### **src/api/routers/ - API Endpoints**

##### **auth.py - Authentication Router**
- `POST /register/customer` - Đăng ký khách hàng mới
- `POST /register/staff` - Đăng ký nhân viên mới
- `POST /login/customer` - Đăng nhập khách hàng
- `POST /login/staff` - Đăng nhập nhân viên
- **Security**: Password hashing với Werkzeug

##### **products.py - Product Management**
- `GET /products` - Lấy danh sách sản phẩm (với search/filter)
- `GET /products/{id}` - Chi tiết sản phẩm
- `GET /products/{id}/inventory` - Inventory của sản phẩm
- `GET /products/{id}/suppliers` - Nhà cung cấp của sản phẩm
- `POST /products` - Tạo sản phẩm mới
- `PUT /products/{id}` - Cập nhật sản phẩm
- `DELETE /products/{id}` - Xóa sản phẩm (kiểm tra ràng buộc)

##### **orders.py - Order Processing**
- `GET /orders` - Danh sách đơn hàng (với filter)
- `GET /orders/{id}` - Chi tiết đơn hàng
- `POST /orders` - Tạo đơn hàng mới
- `PUT /orders/{id}` - Cập nhật đơn hàng
- `DELETE /orders/{id}` - Xóa đơn hàng
- `POST /order/checkout` - Checkout với multiple products

##### **inventory_operations.py - Inventory Management**
- `POST /inventory/import` - Nhập hàng vào kho
- `POST /inventory/export` - Xuất hàng từ kho
- `POST /inventory/stocktaking` - Kiểm kê tồn kho
- **Stock validation**: Kiểm tra số lượng trước khi export

##### **reports.py - Business Intelligence**
- `GET /reports/revenue` - Báo cáo doanh thu
- `GET /reports/top-products` - Top sản phẩm bán chạy
- `GET /reports/inventory` - Báo cáo tồn kho
- `GET /reports/summary` - Tổng hợp KPIs
- `GET /customers/{id}/debts` - Công nợ khách hàng
- `GET /debts` - Tất cả công nợ

##### **Other Routers**
- **customers.py**: CRUD operations cho khách hàng
- **staff.py**: Quản lý nhân viên và phân quyền
- **payments.py**: Xử lý thanh toán
- **vendors.py**: Quản lý nhà cung cấp
- **stores.py**: Lịch sử nhập/xuất kho
- **supplies.py**: Quan hệ sản phẩm - nhà cung cấp

---

## **B. Customer Frontend (React SPA)**

### **1. Prerequisites**
- **Node.js**: 16.0+
- **npm**: 7.0+ (đi kèm với Node.js)

### **2. Installation (Cài đặt)**

#### **Bước 1: Cài đặt dependencies**
```bash
# Từ thư mục gốc của dự án
cd src/client

# Cài đặt tất cả dependencies
npm install
```

#### **Bước 2: Cấu hình API Connection**
Chỉnh sửa `src/client/src/config.js`:
```javascript
// Thay đổi IP và port theo API server
export const API_BASE_URL = "http://192.168.80.70:6868";
```

### **3. Usage (Sử dụng)**

#### **Chạy Development Server**
```bash
# Từ thư mục src/client
npm run dev

# Hoặc từ thư mục gốc
npm run client
```

#### **Build Production**
```bash
npm run build
npm run preview
```

#### **Truy cập ứng dụng**
- **Development**: `http://localhost:5173` (hoặc port khác)
- **Production**: Serve files từ `dist/` folder

### **4. Component Roles & Functions**

#### **src/client/src/App.jsx - Main Application**
- **React Router setup** cho client-side routing
- **Route definitions** cho các trang: Login, Register, Cart, Order History, etc.
- **Authentication state management**
- **Layout components** và navigation

#### **src/client/src/pages/ - Page Components**

##### **Authentication Pages**
- **LoginView.jsx**: Form đăng nhập khách hàng
- **RegisterView.jsx**: Form đăng ký tài khoản mới
- **AccountView.jsx**: Thông tin tài khoản và chỉnh sửa profile

##### **Shopping Pages**
- **CartView.jsx**: Giỏ hàng với add/remove/update items
- **OrderView.jsx**: Trang đặt hàng và checkout
- **OrderHistory.jsx**: Lịch sử đơn hàng đã đặt
- **CustomerView.jsx**: Dashboard khách hàng

##### **Product Browsing**
- **Product listing và detail views**
- **Search và filter functionality**
- **Category browsing**

#### **src/client/src/config.js - API Configuration**
- **API_BASE_URL**: Địa chỉ backend API
- **Centralized configuration** cho tất cả API calls

#### **Key Features**
- **Responsive design** với Tailwind CSS
- **Real-time cart updates**
- **Order tracking**
- **Customer loyalty points**
- **Payment integration**

---

## **C. Manager Frontend (Admin Panel)**

### **1. Installation (Cài đặt)**

#### **Bước 1: Cài đặt dependencies**
```bash
# Từ thư mục gốc của dự án
npm install
```

#### **Bước 2: Cấu hình API Connection**
Chỉnh sửa `src/manager/constants/config.js`:
```javascript
const config = {
    API_BASE_URL: "http://192.168.80.70:6868",
    // ... các endpoints khác
};
```

### **2. Usage (Sử dụng)**

#### **Chạy Manager Interface**
```bash
# Từ thư mục gốc
npm run manager
```

#### **Truy cập Admin Panel**
- **URL**: `http://localhost:5173` (hoặc port configured)

### **3. Component Roles & Functions**

#### **src/manager/App.jsx - Admin Application**
- **Staff authentication** và authorization
- **Admin routing** với protected routes
- **Layout với sidebar navigation**

#### **src/manager/pages/ - Admin Pages**

##### **LoginPage.jsx - Staff Login**
- **Staff authentication form**
- **Role-based access control**

##### **ReportsPage.jsx - Business Reports**
- **Revenue analytics**
- **Inventory reports**
- **Sales performance**
- **Customer insights**

##### **Management Pages (CRUD)**
- **Product management**: Add/edit/delete products
- **Customer management**: View customer data, debts
- **Order management**: Process orders, update status
- **Staff management**: Employee administration
- **Inventory operations**: Import/export/stocktaking

#### **src/manager/constants/config.js - Manager Configuration**
- **API_BASE_URL**: Backend connection
- **API_ENDPOINTS**: Tất cả API endpoints được define centrally
- **Constants** cho dropdowns, status values

#### **src/manager/utils/permissions.js - Access Control**
- **Role-based permissions**
- **Route protection**
- **Action authorization**

#### **Key Features**
- **Comprehensive CRUD operations** cho tất cả entities
- **Advanced reporting** và analytics
- **Inventory management** tools
- **Staff management** system
- **Real-time data updates**

---

## **D. System Architecture & Data Flow**

### **1. Application Layers**
```
Frontend (React) ←HTTP→ Backend (FastAPI) ←SQL→ Database (MySQL)
```

### **2. Authentication Flow**
```
Login Request → FastAPI Router → Database Query → JWT Token → Frontend Storage
```

### **3. Order Processing Flow**
```
Add to Cart → Checkout → Create Order → Process Payment → Update Inventory → Send Confirmation
```

### **4. Inventory Management Flow**
```
Import/Export Request → Validate Stock → Update Database → Log Transaction → Update Reports
```

---

## **E. Troubleshooting & Common Issues**

### **API Issues**
```bash
# Check if API is running
curl http://192.168.80.70:6868/docs

# Check database connection
python -c "import pymysql; print('MySQL OK')"

# Check logs
tail -f api_logs.log
```

### **Frontend Issues**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check console for errors
# F12 → Console tab
```

### **Database Issues**
```sql
-- Check connection
SHOW PROCESSLIST;

-- Check tables
SHOW TABLES;

-- Reset auto_increment
ALTER TABLE tbl_product AUTO_INCREMENT = 1;
```

### **Network Issues**
- **CORS errors**: Check CORS_ALLOW_ORIGINS in config.py
- **Connection refused**: Verify SERVER_HOST and port
- **Firewall**: Allow port 6868 through firewall

---

## **F. Deployment Checklist**

### **Pre-deployment**
- [ ] Update API_BASE_URL in frontend configs
- [ ] Change CORS_ALLOW_ORIGINS to specific domains
- [ ] Set SERVER_RELOAD = False
- [ ] Update database credentials
- [ ] Test all endpoints
- [ ] Build production frontend bundles

### **Production Deployment**
- [ ] Use production WSGI server (gunicorn)
- [ ] Set up reverse proxy (nginx)
- [ ] Configure SSL certificates
- [ ] Set up database backups
- [ ] Configure monitoring and logging

---

## **G. Development Workflow**

### **1. Backend Development**
```bash
# Activate virtual environment
source venv/bin/activate

# Run with auto-reload
uvicorn src.api.main:app --reload

# Test API endpoints
curl -X GET "http://localhost:6868/products"
```

### **2. Frontend Development**
```bash
# Run client
npm run client

# Run manager
npm run manager

# Build for production
npm run build
```

### **3. Database Development**
```sql
-- Create migration scripts
-- Update schema
-- Test queries
-- Backup data
```

This comprehensive guide covers the complete implementation of the Store Management System, including installation, configuration, usage, and detailed component roles.
