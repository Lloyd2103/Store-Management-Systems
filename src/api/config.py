"""
File cấu hình cho backend
Thay đổi các tham số tại đây để cấu hình server và database
"""

# ===== SERVER CONFIG =====
SERVER_HOST = "192.168.2.2"  # Địa chỉ IP hoặc hostname (0.0.0.0 để lắng nghe trên tất cả interfaces)
SERVER_PORT = 6868  # Port của API server
SERVER_RELOAD = True  # Tự động reload khi có thay đổi code (chỉ dùng khi development)

# ===== DATABASE CONFIG =====
DB_CONFIG = {
    "host": "localhost",  # Địa chỉ database server
    "user": "root",  # Username database
    "password": "12345678",  # Password database
    "db": "storemanagesystem",  # Tên database
    # cursorclass sẽ được xử lý tự động trong api.py
}

# ===== CORS CONFIG =====
# Danh sách các origin được phép truy cập API
# Để ["*"] cho phép tất cả (chỉ dùng khi development)
# Trong production nên chỉ định cụ thể: ["http://localhost:1721", "https://yourdomain.com"]
CORS_ALLOW_ORIGINS = ["*"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# ===== LOGGING CONFIG =====
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

