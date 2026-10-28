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

    #getting names from products already in DB, this will be the basis for checking for duplicates.
    cursor.execute("SELECT name FROM products")
    existing_names = {row["name"] for row in cursor.fetchall()}

    #connecting category name with catergory id in dictionary
    category_map = {}
    for cat_name in categories:
        cursor.execute("SELECT category_id FROM categories WHERE name = ?", (cat_name,))
        row = cursor.fetchone()
        if row:
            category_map[cat_name] = row["category_id"]
        else:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (cat_name,))
            category_map[cat_name] = cursor.lastrowid

    for data in products:
        name = data.get('title')
        price = data.get('price')
        cat_name = data.get('category')
        category_id = category_map.get(cat_name)
        
        if name in existing_names:
            print(f"{name} already imported to DB")
            continue

        cursor.execute("INSERT INTO products (name, price, stock, category_id) VALUES (?, ?, ?, ?)", (name, price, 10, category_id))
        
        existing_names.add(name)

    conn.commit()
    conn.close()
    return

imported_products_to_db(products, categories)