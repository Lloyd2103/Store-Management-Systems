# Hướng dẫn cấu hình

Dự án này sử dụng các file config để quản lý cấu hình IP, port và các tham số khác.

## Backend Configuration

File cấu hình backend: `back_end/config.py`

### Các tham số có thể thay đổi:

1. **SERVER_HOST**: Địa chỉ IP hoặc hostname của server
   - `"localhost"` - Chỉ lắng nghe trên localhost
   - `"0.0.0.0"` - Lắng nghe trên tất cả interfaces (để truy cập từ mạng khác)

2. **SERVER_PORT**: Port của API server (mặc định: 6868)

3. **SERVER_RELOAD**: Tự động reload khi có thay đổi code
   - `True` - Bật auto-reload (development)
   - `False` - Tắt auto-reload (production)

4. **DB_CONFIG**: Cấu hình database
   - `host`: Địa chỉ database server
   - `user`: Username database
   - `password`: Password database
   - `db`: Tên database

5. **CORS_ALLOW_ORIGINS**: Danh sách các origin được phép truy cập API
   - `["*"]` - Cho phép tất cả (chỉ dùng khi development)
   - `["http://localhost:1721", "https://yourdomain.com"]` - Chỉ định cụ thể (production)

### Ví dụ cấu hình:

```python
# Development
SERVER_HOST = "localhost"
SERVER_PORT = 6868
CORS_ALLOW_ORIGINS = ["*"]

# Production
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 6868
CORS_ALLOW_ORIGINS = ["https://yourdomain.com"]
```

## Frontend Configuration

File cấu hình frontend: `src/config.js`

### Các tham số có thể thay đổi:

1. **API_BASE_URL**: Địa chỉ API backend
   - `"http://localhost:6868"` - Local development
   - `"http://192.168.2.1:6868"` - Mạng nội bộ
   - `"https://api.yourdomain.com"` - Production

### Ví dụ cấu hình:

```javascript
// Local development
API_BASE_URL: "http://localhost:6868"

// Mạng nội bộ
API_BASE_URL: "http://192.168.2.1:6868"

// Production
API_BASE_URL: "https://api.yourdomain.com"
```

## Vite Configuration

File cấu hình Vite: `vite.config.js`

Port của frontend development server có thể được thay đổi trong file này:

```javascript
server: {
  port: 1721  // Thay đổi port tại đây
}
```

## Cách sử dụng

1. **Thay đổi cấu hình backend**: Chỉnh sửa file `back_end/config.py`
2. **Thay đổi cấu hình frontend**: Chỉnh sửa file `src/config.js`
3. **Khởi động lại server**: Sau khi thay đổi config, khởi động lại cả backend và frontend

## Lưu ý

- Khi thay đổi `SERVER_HOST` thành `"0.0.0.0"`, đảm bảo firewall cho phép kết nối đến port đã cấu hình
- Trong production, nên thay đổi `CORS_ALLOW_ORIGINS` từ `["*"]` sang danh sách cụ thể để bảo mật
- Đảm bảo `API_BASE_URL` trong frontend khớp với `SERVER_HOST` và `SERVER_PORT` của backend

