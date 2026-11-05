import sqlite3
import os
import math
import requests
from pathlib import Path
from dotenv import load_dotenv
from seed import reset_database
from database import imported_products_to_db, list_products_not_part_of_orders
from external_api import get_products_from_FakeStoreApi, get_categories_from_FakeStoreApi
from util import get_request

load_dotenv()

API_KEY = os.getenv("API_KEY")
REST_API_URL = os.getenv("REST_API_URL", "127.0.0.1:8000")

menu = {
    1: ("Quit", "my_quit"),
    2: ("Import products and categories", "import_products_and_categories_from_FakeStoreApi"),
    3: ("Reset database (replaces data with test data)", "reset_test_data"),
    4: ("List products that never been sold", "list_products_never_sold"),
    5: ("List the revenue ordered by category", "fetch_revenue"),
    7: ("Create product via API", "create_product_via_api")
}


def my_quit():
    pass


def fetch_revenue():
    url = f"http://{REST_API_URL}/reports/revenue"
    headers = {"X-API-Key": API_KEY}

    response = get_request(url, headers=headers)

    if response is None:
        return

    data = response.json()

    print("\n--- Report: Revenue per category ---")
    for row in data:
        print(f"Category: {row['category']} | Revenue: ${row['revenue']} (USD)")
    print("------------------------------------\n")
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


def create_product_via_api():
    load_dotenv(Path(__file__).resolve().parent / ".env")
    api_key = os.getenv("API_KEY", "").strip()
    api_url = os.getenv("REST_API_URL", "127.0.0.1:8000").strip().rstrip("/")
    if not api_url.startswith(("http://", "https://")):
        api_url = "http://" + api_url
    if not api_key:
        print("Set API_KEY in your .env file first.")
        return

    name = input("Product name: ").strip()
    category_name = input("Category name: ").strip()
    try:
        price = float(input("Price: "))
        stock = int(input("Stock quantity: "))
    except ValueError:
        print("Enter a number for price and a whole number for stock.")
        return
    if not name or not category_name or len(name) > 100 or len(category_name) > 100:
        print("Product and category names must contain 1 to 100 characters.")
        return
    if not math.isfinite(price) or price < 0 or stock < 0:
        print("Price and stock must be zero or greater, and price must be finite.")
        return

    headers = {"X-API-Key": api_key}
    try:
        response = requests.post(
            api_url + "/categories", headers=headers,
            json={"name": category_name}, timeout=10
        )
        response.raise_for_status()
        category = response.json()

        product = {
            "name": name,
            "category_id": category["category_id"],
            "price": price,
            "stock": stock,
        }
        response = requests.post(
            api_url + "/products", headers=headers, json=product, timeout=10
        )
        if response.status_code == 409:
            print("A product with this name already exists. No product was added.")
            return
        response.raise_for_status()
        created = response.json()
        print(f"Product created successfully. Product ID: {created['product_id']}")
    except requests.HTTPError:
        print(f"API request failed ({response.status_code}). Check your API key and product details.")
    except requests.exceptions.JSONDecodeError:
        print("The API returned an unexpected response.")
    except requests.RequestException:
        print("Could not contact the API. Check REST_API_URL and that the server is running.")
    except (ValueError, KeyError, TypeError, AttributeError):
        print("The API returned an unexpected response.")


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


if __name__ == "__main__":
    main()
