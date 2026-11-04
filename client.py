import sqlite3
from seed import reset_database
from database import imported_products_to_db, list_products_not_part_of_orders
from external_api import get_products_from_FakeStoreApi, get_categories_from_FakeStoreApi
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
REST_API_URL = os.getenv("REST_API_URL", "127.0.0.1:8000")

menu = {
    1: ("Quit", "my_quit"),
    2: ("Import products and categories", "import_products_and_categories_from_FakeStoreApi"),
    3: ("Reset database (replaces data with test data)", "reset_test_data"),
    4: ("List products that never been sold", "list_products_never_sold"),
    5: ("List the revenue ordered by category", "fetch_revenue")
}


def my_quit():
    pass

def fetch_revenue():
    url = f"http://{REST_API_URL}/reports/revenue"
    headers = {"X-API-Key": API_KEY}

    try:
        response = requests.get(url, headers = headers, timeout = 2)
    
        if response.status_code == 200:
            data = response.json()
            print("\n- Report: revenue per category -")
            for row in data:
                print(f"Category: {row['category']} | Revenue: ${row['revenue']} (USD)")
            print("-------------------------------\n")
        elif response.status_code == 401:
            print("Error: incorrect or missing API-key.")
        else:
            print(f"Error: {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to {REST_API_URL}. Is the server running?")
    pass

def import_products_and_categories_from_FakeStoreApi():
    products = get_products_from_FakeStoreApi()
    categories = get_categories_from_FakeStoreApi()
    imported_products_to_db(products, categories)
    # TODO: check if we already have these products / categories in the database
    # TODO: each product / category not already in database should be saved in database


def reset_test_data():
    confirmation = input(
        'This deletes all data in the five shop tables. Type "yes" to continue: '
    )
    if confirmation.strip().lower() != 'yes':
        print("Reset cancelled.")
        return

    try:
        path = reset_database()
    except (sqlite3.Error, OSError) as error:
        print(f"Could not reset database: {error}")
    else:
        print(f"Database reset with test data: {path}")


def list_products_never_sold():
    try:
        products = list_products_not_part_of_orders()

    except sqlite3.Error as error:
        print(f"Database Error: {error}")
        return

    if not products:
        print("No products found")
        return

    print(
        f"{"product_id":^15} {"name":<100} {"category":<10}")
    for product in products:
        print(
            f"{product["product_id"]:^15} {product["name"]:<100} {product["category"]:<10}")


def main():
    choice = None
    while (choice != 1):
        for key, value in sorted(menu.items()):
            print(f'{key} {value[0]}')
        try:
            choice = int(input())
            if not choice in menu.keys():
                print("invalid menu number")
                choice = None
        except Exception as e:
            print(e)
            choice = None
        if choice:
            chosen = menu[choice][1]
            globals()[chosen]()


main()
