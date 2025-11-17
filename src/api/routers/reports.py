from typing import Optional
from fastapi import APIRouter, HTTPException
import logging

from ..db import fetchall_sql
from .. import queries

router = APIRouter()

@router.get("/reports/revenue")
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
        query = queries.SELECT_REVENUE_REPORT.format(where_clause=where_clause)
        return fetchall_sql(query, tuple(params) if params else ())
    except Exception as e:
        logging.error(f"Error in get_revenue_report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/top-products")
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
        
        query = queries.SELECT_TOP_PRODUCTS_REPORT.format(where_clause=where_clause)
        return fetchall_sql(query, tuple(params_list))
    except Exception as e:
        logging.error(f"Error in get_top_products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/inventory")
def get_inventory_report():
    try:
        return fetchall_sql(queries.SELECT_INVENTORY_REPORT)
    except Exception as e:
        logging.error(f"Error in get_inventory_report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/summary")
def get_summary_report():
    try:
        # Tổng hợp các thống kê chính
        summary = {}
        
        summary['totalCustomers'] = fetchall_sql(queries.SUMMARY_TOTAL_CUSTOMERS)[0]['count']
        summary['totalProducts'] = fetchall_sql(queries.SUMMARY_TOTAL_PRODUCTS)[0]['count']
        summary['totalOrders'] = fetchall_sql(queries.SUMMARY_TOTAL_ORDERS)[0]['count']
        
        revenue = fetchall_sql(queries.SUMMARY_TOTAL_REVENUE)
        summary['totalRevenue'] = revenue[0]['total'] or 0
        
        debts = fetchall_sql(queries.SUMMARY_TOTAL_DEBTS)
        summary['totalDebts'] = debts[0]['total'] or 0
        
        inventory = fetchall_sql(queries.SUMMARY_TOTAL_INVENTORY_VALUE)
        summary['totalInventoryValue'] = inventory[0]['total'] or 0
        
        return summary
    except Exception as e:
        logging.error(f"Error in get_summary_report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
def get_categories():
    try:
        return fetchall_sql(queries.SELECT_CATEGORIES)
    except Exception as e:
        logging.error(f"Error in get_categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories/products")
def get_products_by_category():
    try:
        return fetchall_sql(queries.SELECT_PRODUCTS_BY_CATEGORY)
    except Exception as e:
        logging.error(f"Error in get_products_by_category: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customers/{id}/debts")
def get_customer_debts(id: int):
    try:
        return fetchall_sql(queries.SELECT_CUSTOMER_DEBTS, (id,))
    except Exception as e:
        logging.error(f"Error in get_customer_debts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debts")
def get_all_debts():
    try:
        return fetchall_sql(queries.SELECT_ALL_DEBTS)
    except Exception as e:
        logging.error(f"Error in get_all_debts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
