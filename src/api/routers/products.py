from typing import Optional
from fastapi import APIRouter, HTTPException, status
import logging

from ..db import fetchall_sql, execute_sql, get_connection, safe_close_connection
from ..models.product import Product
from .. import queries

router = APIRouter()

def check_product_usage(product_id: int) -> dict:
    """Kiểm tra xem product có đang được sử dụng trong orders, stores, supplies không"""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Kiểm tra trong orders (tbl_requests)
            cursor.execute(queries.CHECK_PRODUCT_IN_REQUESTS, (product_id,))
            orders_count = cursor.fetchone()['count']
            
            # Kiểm tra trong stores
            cursor.execute(queries.CHECK_PRODUCT_IN_STORES, (product_id,))
            stores_count = cursor.fetchone()['count']
            
            # Kiểm tra trong supplies
            cursor.execute(queries.CHECK_PRODUCT_IN_SUPPLIES, (product_id,))
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

@router.get("/products")
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
            return fetchall_sql(queries.SELECT_PRODUCTS)
    except Exception as e:
        logging.error(f"Error in get_products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{id}")
def get_product(id: int):
    try:
        rows = fetchall_sql(queries.SELECT_PRODUCT_BY_ID, (id,))
        if not rows:
            raise HTTPException(status_code=404, detail="Product not found")
        return rows[0]
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in get_product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{id}/inventory")
def get_product_inventory(id: int):
    """Lấy thông tin inventory của một product"""
    try:
        return fetchall_sql(queries.SELECT_PRODUCT_INVENTORY, (id,))
    except Exception as e:
        logging.error(f"Error in get_product_inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{id}/suppliers")
def get_product_suppliers(id: int):
    """Lấy thông tin suppliers của một product"""
    try:
        return fetchall_sql(queries.SELECT_PRODUCT_SUPPLIERS, (id,))
    except Exception as e:
        logging.error(f"Error in get_product_suppliers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(payload: Product):
    try:
        product_id = execute_sql(queries.INSERT_PRODUCT, (
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

@router.put("/products/{id}")
def update_product(id: int, payload: Product):
    try:
        execute_sql(queries.UPDATE_PRODUCT, (
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

@router.delete("/products/{id}")
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
        
        execute_sql(queries.DELETE_PRODUCT, (id,))
        return {"message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in delete_product: {e}")
        raise HTTPException(status_code=500, detail=str(e))