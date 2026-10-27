#connection to SQL queries
from external_api import get_json
import pprint
import sqlite3

base_url = "https://fakestoreapi.com/"
products_from_external_api = get_json(base_url + "products")

def imported_products_to_db(api_products):
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    imported = 0 #counters for status return
    updated = 0

    for data in api_products:
        name = data.get('title') #naming convention from ER-diagram
        price = data.get('price')
        category = data.get('category')
        default_stock = 10 #there's no stock in the fake store, how to deal with this?

        cursor.execute("SELECT product_id, stock FROM products WHERE name = ?", (name,))
        existing_product = cursor.fetchone()

        if existing_product: #already existing product
            print(f"{name} already exists")
            
            """ new_stock = existing_product['stock'] + default_stock
            cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, existing_product["id"]))
            updated_count += 1 """

        else: #not already existing product
            cursor.execute("INSERT INTO products (name, price, category_id, stock) VALUES (?, ?, ?, ?)",
                (name, price, category, default_stock)
            )
            imported += 1

    conn.commit()
    conn.close()
    
    return{"imported": imported, "updated": updated}