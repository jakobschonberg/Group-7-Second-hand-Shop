from client_helper import get_request
import requests


def get_products_from_FakeStoreApi() -> list[dict]:
    result = get_request("https://fakestoreapi.com/products")
    if type(result) == requests.models.Response and result.status_code == 200:
        return result.json()
    return []


def get_categories_from_FakeStoreApi() -> list[dict]:
    result = get_request("https://fakestoreapi.com/products/categories")
    if type(result) == requests.models.Response and result.status_code == 200:
        return result.json()
    return []
