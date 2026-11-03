# builds database and adds test data
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv


CATEGORIES = [
    (1, 'Clothing'),
    (2, 'Electronics'),
    (3, 'Shoes'),
    (4, 'Accessories'),

]
PRODUCTS = [
    (1, 1, 'White T-shirt', 50.0, 10),
    (2, 1, 'Winter jacket', 250.0, 0),
    (3, 2, 'USB keyboard', 80.0, 1),
    (4, 2, 'Wired headphones', 0.0, 5),
    (5, 3, 'Running shoes', 150.0, 3),
    (6, 4, 'Scarf', 220.0, 3),
]
CUSTOMERS = [
    (1, 'Ada', 'ada@example.com', None, None),
    (2, 'Sam', 'sam@example.com', '+46700000000', 'Stockholm'),
    (3, "Alex O'Neil", 'alex@example.com', None, 'Uppsala'),
    (4, 'Zoë', 'zoe@example.com', '0700000001', None),
]
ORDERS = [
    (1, 1, 'NEW', '2026-10-26'),
    (2, 2, 'DELIVERED', '2026-10-27'),
    (3, 2, 'CANCELLED', '2026-10-28'),
    (4, 3, 'DELIVERED', '2018-01-01'),
    (5, 4, 'NEW', '2025-04-01'),
    (6, 4, 'DELIVERED', '2024-09-01'),
    (7, 3, 'DELIVERED', '2025-10-01'),
    (8, 3, 'CANCELLED', '2025-10-01'),

]
ORDER_ITEMS = [
    (1, 1, 50.0, 1),
    (2, 1, 45.0, 2),
    (2, 2, 250.0, 1),
    (3, 3, 80.0, 1),
    (4, 4, 0.0, 1),
    (5, 5, 150.0, 2),
    (5, 6, 220.0, 3),
    (6, 5, 150.0, 3),
    (7, 6, 220.0, 1),
    (8, 6, 220.0, 1),
]


def reset_database(database_path=None):
    project_folder = Path(__file__).resolve().parent
    env_file = project_folder / '.env'
    load_dotenv(dotenv_path=env_file)

    if database_path is None:
        database_path = os.getenv('DATABASE_PATH', 'shop.db')

    database_file = Path(database_path).resolve()
    schema_file = project_folder / 'db_schema.sql'
    schema_sql = schema_file.read_text()

    conn = sqlite3.connect(database_file)
    try:
        conn.execute('PRAGMA foreign_keys = ON')
        reset_sql = '''
            BEGIN IMMEDIATE;
            DROP TABLE IF EXISTS order_items;
            DROP TABLE IF EXISTS orders;
            DROP TABLE IF EXISTS products;
            DROP TABLE IF EXISTS customers;
            DROP TABLE IF EXISTS categories;
        '''
        conn.executescript(reset_sql + schema_sql)

        conn.executemany(
            'INSERT INTO categories (category_id, name) VALUES (?, ?)',
            CATEGORIES,
        )
        conn.executemany(
            'INSERT INTO products '
            '(product_id, category_id, name, price, stock) VALUES (?, ?, ?, ?, ?)',
            PRODUCTS,
        )
        conn.executemany(
            'INSERT INTO customers '
            '(customer_id, name, email, phone_no, city) VALUES (?, ?, ?, ?, ?)',
            CUSTOMERS,
        )
        conn.executemany(
            'INSERT INTO orders '
            '(order_id, customer_id, status, order_date) VALUES (?, ?, ?, ?)',
            ORDERS,
        )
        conn.executemany(
            'INSERT INTO order_items '
            '(order_id, product_id, unit_price, quantity) VALUES (?, ?, ?, ?)',
            ORDER_ITEMS,
        )
        relationship_errors = conn.execute(
            'PRAGMA foreign_key_check'
        ).fetchall()

        if relationship_errors:
            raise sqlite3.IntegrityError('Test data has invalid relationships')
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return database_file
