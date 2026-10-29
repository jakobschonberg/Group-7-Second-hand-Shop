# connection to SQL queries
import sqlite3
from pathlib import Path
from contextlib import contextmanager
import os
from external_api import get_products_from_FakeStoreApi, get_categories_from_FakeStoreApi

products = get_products_from_FakeStoreApi()
categories = get_categories_from_FakeStoreApi()


@contextmanager
def connection():
    path = Path(os.getenv("DATABASE_PATH", "shop.db")).resolve()
    conn = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        with conn:
            yield conn
            conn.commit()
    finally:
        conn.close()


def imported_products_to_db(products, categories):
    with connection() as conn:
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

        category_map = {row["name"]: row["category_id"]
                        for row in cursor.fetchall()}

        product_dicts = []
        for product in products:
            product_dicts.append({"name": product.get('title'),
                                  "price": product.get('price'),
                                  "stock": 10,
                                  "category_id": category_map.get(product.get('category'))
                                  })

        cursor.executemany("""
        INSERT OR IGNORE INTO products (name, price, stock, category_id) 
        VALUES (:name, :price, :stock, :category_id)
        """, product_dicts)

        return


imported_products_to_db(products, categories)


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


def create_product(product: dict):
    with connection() as conn:
        cursor = conn.execute("INSERT INTO products(name,category_id,price,stock) VALUES (?,?,?,?)",
                              (product['name'], product['category_id'], product['price'], product['stock']))

        print(f"{cursor.lastrowid} is created")
        return cursor.lastrowid


def update_product(product_id: int, product: dict):
    with connection() as conn:
        cursor = conn.execute(
            "UPDATE products SET name=?,category_id=?,price=?,stock=? WHERE product_id=?",
            (product['name'], product['category_id'],
             product['price'], product['stock'], product_id)
        )
        print(f"{cursor.rowcount} is updated")
        return cursor.rowcount > 0


def delete_product(product_id: int):
    with connection() as conn:
        cursor = conn.execute(
            "DELETE FROM products WHERE product_id=?", (product_id,)
        )
        print(f"{cursor.rowcount} is deleted")
        return cursor.rowcount > 0


def search_product(product_id: int):
    with connection() as conn:
        product = conn.execute(
            "SELECT product_id,name, category_id,price,stock FROM products WHERE product_id=?", (
                product_id,)
        ).fetchone()

        if product is None:
            return None
        print(f"{product} found")
        return dict(product)
