import sqlite3
from seed import reset_database
from external_api import get_products_from_FakeStoreApi, get_categories_from_FakeStoreApi



menu = {
    1:("Quit", "my_quit"),
    2:("Import products and categories", "import_products_and_categories_from_FakeStoreApi"),
    3:("Reset database (replaces data with test data)", "reset_test_data")
}

def my_quit():
    pass

def import_products_and_categories_from_FakeStoreApi():
    from database import imported_products_to_db

    products = get_products_from_FakeStoreApi()
    categories = get_categories_from_FakeStoreApi()
    imported_products_to_db(products, categories)
    #TODO: check if we already have these products / categories in the database
    #TODO: each product / category not already in database should be saved in database


def reset_test_data():
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

main()