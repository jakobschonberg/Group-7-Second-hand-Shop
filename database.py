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