import pymysql
from pymysql.cursors import DictCursor
import logging
from .config import DB_CONFIG as CONFIG_DB_CONFIG

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
