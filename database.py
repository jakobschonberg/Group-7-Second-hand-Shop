#connection to SQL queries
from external_api import get_products_from_FakeStoreApi, get_categories_from_FakeStoreApi
import pprint
import sqlite3

products = get_products_from_FakeStoreApi()
categories = get_categories_from_FakeStoreApi()

def imported_products_to_db(products, categories):
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    category_dicts = [{"name": cat} for cat in categories]

    cursor.executemany("""
        INSERT OR IGNORE INTO categories (name)
        VALUES (:name)
        """, category_dicts)
    
    cursor.execute("""
        SELECT category_id, name
        FROM categories
        """)

    category_map ={row["name"]: row["category_id"] for row in cursor.fetchall()}

    product_dicts = []
    for product in products:
        product_dicts.append({"name" : product.get('title'),
                              "price": product.get('price'),
                              "stock": 10,
                              "category_id": category_map.get(product.get('category'))
                              })

    cursor.executemany("""
    INSERT OR IGNORE INTO products (name, price, stock, category_id) 
    VALUES (:name, :price, :stock, :category_id)
    """, product_dicts)

    conn.commit()
    conn.close()
    return

imported_products_to_db(products, categories)
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def connection():
    path = Path(os.getenv("DATABASE_PATH", "shop.db")).resolve()
    conn = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def list_customers():
    with connection() as conn:
        rows = conn.execute(
            "SELECT customer_id, name, email, phone_no, city "
            "FROM customers ORDER BY customer_id"
        ).fetchall()
        return [dict(row) for row in rows]


def create_customer(data):
    with connection() as conn:
        cursor = conn.execute(
            "INSERT INTO customers (name, email, phone_no, city) "
            "VALUES (?, ?, ?, ?)",
            (data["name"], data["email"], data["phone_no"], data["city"]),
        )
        return {"customer_id": cursor.lastrowid, **data}


def update_customer(customer_id, data):
    with connection() as conn:
        cursor = conn.execute(
            "UPDATE customers SET name = ?, email = ?, phone_no = ?, "
            "city = ? WHERE customer_id = ?",
            (data["name"], data["email"], data["phone_no"],
             data["city"], customer_id),
        )
        if not cursor.rowcount:
            return None
        return {"customer_id": customer_id, **data}


def delete_customer(customer_id):
    with connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        if conn.execute(
            "SELECT 1 FROM orders WHERE customer_id = ? LIMIT 1",
            (customer_id,),
        ).fetchone():
            raise ValueError("Customer has orders")
        cursor = conn.execute(
            "DELETE FROM customers WHERE customer_id = ?", (customer_id,)
        )
        return cursor.rowcount > 0
