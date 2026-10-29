import sqlite3
from contextlib import contextmanager


@contextmanager
def connect_db():
    conn = sqlite3.connect("second_hand_shop.db")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_product(product: dict):
    with connect_db() as conn:
        cursor = conn.execute("INSERT INTO products(name,category_id,price,stock) VALUES (?,?,?,?)",
                              (product['name'], product['category_id'], product['price'], product['stock']))

        print(f"{cursor.lastrowid} is created")
        return cursor.lastrowid


def update_product(product_id: int, product: dict):
    with connect_db() as conn:
        cursor = conn.execute(
            "UPDATE products SET name=?,category_id=?,price=?,stock=? WHERE product_id=?",
            (product['name'], product['category_id'],
             product['price'], product['stock'], product_id)
        )
        print(f"{cursor.rowcount} is updated")
        return cursor.rowcount > 0


def delete_product(product_id: int):
    with connect_db() as conn:
        cursor = conn.execute(
            "DELETE FROM products WHERE product_id=?", (product_id,)
        )
        print(f"{cursor.rowcount} is deleted")
        return cursor.rowcount > 0


def search_product(product_id: int):
    with connect_db() as conn:
        product = conn.execute(
            "SELECT product_id,name, category_id,price,stock FROM products WHERE product_id=?", (
                product_id,)
        ).fetchone()

        if product is None:
            return None
        print(f"{product} found")
        return dict(product)
