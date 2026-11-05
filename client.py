import shop_api_client
import math
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
PAGE_SIZE = 2

menu = {
    1: ("Quit", "my_quit"),
    2: ("Import products and categories", "import_products_and_categories_from_FakeStoreApi"),
    3: ("Reset database (replaces data with test data)", "reset_test_data"),
    4: ("List products that never been sold", "list_products_never_sold"),
    5: ("List the revenue ordered by category", "fetch_revenue"),
    6: ("List all products", "list_products_page"),
}


def my_quit():
    pass


def fetch_revenue():
    url = f"http://{REST_API_URL}/reports/revenue"
    headers = {"X-API-Key": API_KEY}

    try:
        response = requests.get(url, headers=headers, timeout=2)

        if response.status_code == 200:
            data = response.json()
            print("\n- Report: revenue per category -")
            for row in data:
                print(
                    f"Category: {row['category']} | Revenue: ${row['revenue']} (USD)")
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


def list_products_page():
    options = ["[N]ext", "[P]revious", "[Number] select", "[B]ack"]
    offset = 0
    while (True):
        products_page = shop_api_client.get_products_page(PAGE_SIZE, offset)
        if products_page is None:
            print("Could not load the product. Please try again later")
            return

        total = products_page["total"]
        total_pages = math.ceil(total/PAGE_SIZE)
        current_page = offset // PAGE_SIZE + 1

        products = products_page["products"]
        if not products:
            if offset > 0:
                offset = max(0, offset - PAGE_SIZE)
                continue
            print("No products available in store now")
            return

        display_products_table(total_pages, current_page, products)

        choice = input(" ".join(options) + ":").strip().lower()
        if choice == "n":
            has_next = offset + PAGE_SIZE < total
            if (has_next):
                offset = offset + PAGE_SIZE
            else:
                print("No next page")
        elif choice == "p":
            has_prev = offset > 0
            if (has_prev):
                offset = offset - PAGE_SIZE
            else:
                print("No Previous page")
        elif choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(products):
                select_product(products[index])
            else:
                print("No product with that number")

        elif choice == "b":
            return
        else:
            print("Invalid choice")


def display_products_table(total_pages, current_page, products):
    print(f"Page {current_page} of {total_pages}")
    print(
        f"{"No":^5} {"Name":<50} {"Category":<20} {"Price":^10} {"Stock":^10}")
    for line_item, product in enumerate(products, 1):
        print(
            f"{line_item:^5} {product["name"]:<50} {product["category_name"]:<20} {product["price"]:^10} {product["stock"]:^10}")


def select_product(product):
    print(f"Selected: {product["name"]} (price {product["price"]})")
    options = ["[U]pdate price", "[D]elete", "[B]ack"]
    choice = input(" ".join(options) + ":").strip().lower()

    if choice == "u":
        update_product_price(product)

    elif choice == "d":
        delete_selected_product(product)
        return

    elif choice == "b":
        return
    else:
        print("Invalid choice")


def update_product_price(product):
    try:
        new_price = float(input("Enter new price: ").strip())
        if not math.isfinite(new_price) or new_price < 0:
            raise ValueError
    except ValueError:
        print("Price must be 0 or more")
        return

    response = shop_api_client.change_price(
        product["product_id"], new_price)

    if response is None:
        return
    status_code = response.status_code
    if status_code == 200:
        print("Product updated successfully")
    elif status_code == 404:
        print("Product not found")
    elif status_code == 401:
        print("Unauthorized")
    elif status_code == 422:
        print("Invalid price")
    else:
        print("Product update not successful")


def delete_selected_product(product):
    confirm = input(
        f"Do you really want to delete the product {product["name"]}. Type 'yes' to continue : ").strip().lower()
    if confirm in ("yes", "y"):
        response = shop_api_client.delete_product(product["product_id"])
        if response is None:
            return
        status_code = response.status_code
        if status_code == 204:
            print("Product deleted successfully")
        elif status_code == 404:
            print("Product not found")
        elif status_code == 401:
            print("Unauthorized")
        elif status_code == 409:
            print("Product cannot be deleted. Related records exist")
        else:
            print("product deletion not successful")
    else:
        print("Delete Cancelled")


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
