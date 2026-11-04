import math
import sqlite3
from seed import reset_database
from database import imported_products_to_db, list_products_not_part_of_orders
from external_api import get_products_from_FakeStoreApi, get_categories_from_FakeStoreApi
import shop_api_client

PAGE_SIZE = 2

menu = {
    1: ("Quit", "my_quit"),
    2: ("Import products and categories", "import_products_and_categories_from_FakeStoreApi"),
    3: ("Reset database (replaces data with test data)", "reset_test_data"),
    4: ("List products that never been sold", "list_products_never_sold"),
    5: ("List all products", "list_products_page"),
}


def my_quit():
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
            print("No products available in store now")
            return

        print(f"Page {current_page} of {total_pages}")
        print(
            f"{"No":^5} {"Name":<50} {"Category":<20} {"Price":^10} {"Stock":^10}")
        for line_item, product in enumerate(products, 1):
            print(
                f"{line_item:^5} {product["name"]:<50} {product["category_name"]:<20} {product["price"]:^10} {product["stock"]:^10}")

        choice = input(" ".join(options) + ":").strip().lower()
        if choice == 'n':
            has_next = offset + PAGE_SIZE < total
            if (has_next):
                offset = offset + PAGE_SIZE
            else:
                print("No next page")
        elif choice == 'p':
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

        elif choice == 'b':
            return
        else:
            print("Invalid choice")


def select_product(product):
    print(f"Selected: {product["name"]} (price {product["price"]})")
    options = ["[C]hange price", "[D]elete", "[B]ack"]
    choice = input(" ".join(options) + ":").strip().lower()

    if choice == 'c':
        print("change price - yet to be iplemented")
    elif choice == 'd':
        print("delete - yet to be implemented")
    elif choice == 'b':
        return
    else:
        print("Invalid choice")


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
