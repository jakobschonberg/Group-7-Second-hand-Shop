from seed import reset_database
from database import imported_products_to_db, list_products_not_part_of_orders
from external_api import get_products_from_FakeStoreApi, get_categories_from_FakeStoreApi
import sqlite3

menu = {
    1: ("Quit", "my_quit"),
    2: ("Import products and categories", "import_products_and_categories_from_FakeStoreApi"),
    3: ("Reset database (replaces data with test data)", "reset_test_data"),
    4: ("List products that never been sold", "list_products_never_sold")
}

def my_quit():
    pass

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

def import_products_and_categories_from_FakeStoreApi():
    products = get_products_from_FakeStoreApi()
    categories = get_categories_from_FakeStoreApi()
    imported_products_to_db(products, categories)

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