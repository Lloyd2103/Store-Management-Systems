import sys
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

# Add the project root to the Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)


# Import config
from src.api.config import (
    SERVER_HOST, SERVER_PORT, SERVER_RELOAD,
    CORS_ALLOW_ORIGINS, CORS_ALLOW_CREDENTIALS, CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS,
    LOG_LEVEL
)

# Import routers
from src.api.routers import (
    customers, products, orders, payments, staff, vendors, inventory,
    requests, stores, supplies, reports, auth, inventory_operations
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

# Include routers
app.include_router(customers.router, tags=["Customers"])
app.include_router(products.router, tags=["Products"])
app.include_router(orders.router, tags=["Orders"])
app.include_router(payments.router, tags=["Payments"])
app.include_router(staff.router, tags=["Staff"])
app.include_router(vendors.router, tags=["Vendors"])
app.include_router(inventory.router, tags=["Inventory"])
app.include_router(requests.router, tags=["Requests"])
app.include_router(stores.router, tags=["Stores"])
app.include_router(supplies.router, tags=["Supplies"])
app.include_router(reports.router, tags=["Reports"])
app.include_router(auth.router, tags=["Authentication"])
app.include_router(inventory_operations.router, tags=["Inventory Operations"])


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
    uvicorn.run("src.api.main:app", host=SERVER_HOST, port=SERVER_PORT, reload=SERVER_RELOAD)