# connection to SQL queries
import sqlite3
from pathlib import Path
from contextlib import contextmanager
import os
from datetime import datetime, timedelta
from collections import defaultdict
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


def get_all_categories_from_db() -> list[dict]:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_all_products_from_db() -> list[dict]:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_receipt_from_db(order_id) -> list[dict]:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.order_date, oi.order_id, p.name, oi.quantity, oi.unit_price, ROUND(oi.quantity * oi.unit_price, 2) AS row_price 
            FROM order_items oi 
            JOIN orders o ON o.order_id = oi.order_id 
            JOIN products p ON p.product_id = oi.product_id 
            WHERE oi.order_id = ? """, (order_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


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

        category_map = {row["name"].lower(): row["category_id"]
                        for row in cursor.fetchall()}

        product_dicts = []
        for product in products:
            product_dicts.append({"name": product.get('title'),
                                  "price": product.get('price'),
                                  "stock": 10,
                                  "category_id": category_map.get((product.get('category') or '').lower())
                                  })

        cursor.executemany("""
        INSERT OR IGNORE INTO products (name, price, stock, category_id) 
        VALUES (:name, :price, :stock, :category_id)
        """, product_dicts)

        return


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

        customer_exists = conn.execute(
            "SELECT 1 FROM customers WHERE customer_id = ?",
            (customer_id,)
        ).fetchone()

        if not customer_exists:
            return False

        cutoff_date = (datetime.now() - timedelta(days=7*365)
                       ).strftime("%Y-%m-%d")

        has_recent_orders = conn.execute(
            "SELECT 1 FROM orders WHERE customer_id = ? AND order_date >= ? LIMIT 1",
            (customer_id, cutoff_date)
        ).fetchone()

        if has_recent_orders:
            conn.execute(
                "UPDATE customers SET name = ?, email = ?, phone_no = ?, city = ? WHERE customer_id = ?",
                ("Anonymiserad Kund",
                 f"deleted_{customer_id}@anonymized.com", None, None, customer_id)
            )
            conn.execute(
                """
                DELETE FROM order_items 
                WHERE order_id IN (
                    SELECT order_id FROM orders WHERE customer_id = ? AND order_date < ?
                )
                """,
                (customer_id, cutoff_date)
            )
            conn.execute(
                "DELETE FROM orders WHERE customer_id = ? AND order_date < ?",
                (customer_id, cutoff_date)
            )
            return "pseudonymized"

        else:
            conn.execute(
                """
                DELETE FROM order_items 
                WHERE order_id IN (
                    SELECT order_id FROM orders WHERE customer_id = ?
                )
                """,
                (customer_id,)
            )
            conn.execute(
                "DELETE FROM orders WHERE customer_id = ?", (customer_id,))

            cursor = conn.execute(
                "DELETE FROM customers WHERE customer_id = ?", (customer_id,))
            return "deleted"


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


def list_products_not_part_of_orders():
    with connection() as conn:
        rows = conn.execute(
            """
            SELECT p.product_id, p.name, c.name as category
            FROM products p
            JOIN categories c ON p.category_id = c.category_id 
            WHERE NOT EXISTS (
                SELECT 1 
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id 
                WHERE oi.product_id = p.product_id AND o.status != 'CANCELLED'
            )
            ORDER BY p.product_id
            """
        ).fetchall()

        return [dict(product) for product in rows]


def get_customer_full_data(customer_id: int):
    with connection() as conn:

        customer_row = conn.execute(
            "SELECT * FROM customers WHERE customer_id = ?", (customer_id,)).fetchone()

        if not customer_row:
            return None

        customer_data = dict(customer_row)

        order_rows = conn.execute(
            "SELECT order_id, status, order_date FROM orders WHERE customer_id = ?",
            (customer_id,)
        ).fetchall()

        if not order_rows:
            customer_data["orders"] = []
            return customer_data

        order_ids = [order["order_id"] for order in order_rows]

        placeholders = ",".join("?" for order_id in order_ids)
        item_rows = conn.execute(
            f"""
                SELECT oi.order_id, p.name, oi.quantity, oi.unit_price 
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id IN ({placeholders})
                ORDER BY oi.order_id
            """,
            order_ids
        ).fetchall()

        items_by_order = defaultdict(list)

        for item in item_rows:
            items_by_order[item["order_id"]].append({
                "name": item["name"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"]
            })

        orders = []
        for order in order_rows:
            ord_id = order["order_id"]
            orders.append({
                "order_id": ord_id,
                "status": order["status"],
                "order_date": order["order_date"],
                "items": items_by_order[ord_id]
            })

        customer_data["orders"] = orders

        return customer_data


def read_order(conn, order_id):
    row = conn.execute(
        "SELECT order_id, customer_id, status, order_date FROM orders "
        "WHERE order_id = ?", (order_id,)
    ).fetchone()
    if row is None:
        return None
    order = dict(row)
    items = conn.execute(
        "SELECT product_id, quantity, unit_price FROM order_items "
        "WHERE order_id = ? ORDER BY product_id", (order_id,)
    ).fetchall()
    order["items"] = [dict(item) for item in items]
    return order


def get_order(order_id):
    with connection() as conn:
        return read_order(conn, order_id)


def list_orders(customer_id=None):
    with connection() as conn:
        if customer_id is None:
            rows = conn.execute(
                "SELECT order_id FROM orders ORDER BY order_id"
            ).fetchall()
        else:
            customer = conn.execute(
                "SELECT 1 FROM customers WHERE customer_id = ?", (customer_id,)
            ).fetchone()
            if customer is None:
                raise LookupError("Customer not found")
            rows = conn.execute(
                "SELECT order_id FROM orders WHERE customer_id = ? "
                "ORDER BY order_id", (customer_id,)
            ).fetchall()
        return [read_order(conn, row["order_id"]) for row in rows]


def create_order(data):
    with connection() as conn:
        # Lock before checking stock so two orders cannot buy the same last item.
        conn.execute("BEGIN IMMEDIATE")
        customer = conn.execute(
            "SELECT 1 FROM customers WHERE customer_id = ?",
            (data["customer_id"],)
        ).fetchone()
        if customer is None:
            raise LookupError("Customer not found")

        cursor = conn.execute(
            "INSERT INTO orders (customer_id, status, order_date) "
            "VALUES (?, 'NEW', date('now'))", (data["customer_id"],)
        )
        order_id = cursor.lastrowid
        quantities = {}
        for item in data["items"]:
            product_id = item["product_id"]
            quantities[product_id] = (
                quantities.get(product_id, 0) + item["quantity"]
            )

        for product_id, quantity in quantities.items():
            product = conn.execute(
                "SELECT price, stock FROM products WHERE product_id = ?",
                (product_id,)
            ).fetchone()
            if product is None:
                raise LookupError(f"Product {product_id} not found")
            if product["stock"] == 0:
                raise ValueError(
                    "Selected product is out of stock. Please continue shopping with other available products."
                )
            if product["stock"] < quantity:
                raise ValueError(f"Not enough stock for product {product_id}")
            conn.execute(
                "INSERT INTO order_items "
                "(order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (order_id, product_id, quantity, product["price"])
            )
            conn.execute(
                "UPDATE products SET stock = stock - ? WHERE product_id = ?",
                (quantity, product_id)
            )
        return read_order(conn, order_id)


def update_order_status(order_id, status):
    with connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        order = read_order(conn, order_id)
        if order is None:
            raise LookupError("Order not found")
        if status == order["status"]:
            return order
        if order["status"] != "NEW":
            raise ValueError("Only NEW orders can change status")
        if status == "CANCELLED":
            for item in order["items"]:
                conn.execute(
                    "UPDATE products SET stock = stock + ? WHERE product_id = ?",
                    (item["quantity"], item["product_id"])
                )
        conn.execute(
            "UPDATE orders SET status = ? WHERE order_id = ?",
            (status, order_id)
        )
        return read_order(conn, order_id)


def get_revenue_per_category():
    with connection() as conn:
        rows = conn.execute(
            """
            SELECT c.name AS category,ROUND(SUM(oi.unit_price * oi.quantity),2) AS revenue 
            FROM products p
            JOIN order_items oi ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            JOIN categories c ON p.category_id = c.category_id
            WHERE o.status != 'CANCELLED'
            GROUP BY c.category_id
            ORDER BY revenue DESC

            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_or_create_category(name):
    with connection() as conn:
        conn.execute(
            "INSERT INTO categories (name) VALUES (?) "
            "ON CONFLICT(name) DO NOTHING", (name,)
        )
        row = conn.execute(
            "SELECT category_id, name FROM categories WHERE name = ?",
            (name,)
        ).fetchone()
        return dict(row)
