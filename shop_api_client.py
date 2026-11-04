from os import getenv
from dotenv import load_dotenv
import requests
from external_api import get_request

load_dotenv()
REST_API_URL = getenv("REST_API_URL", "http://127.0.0.1:8000")
API_KEY = getenv("API_KEY")
PRODUCTS_URL = REST_API_URL + "/products"
HEADERS = {"X-API-Key": API_KEY}


def get_products_page(limit: int, offset: int):

    response = get_request(
        PRODUCTS_URL,
        params={"limit": limit, "offset": offset},
        headers=HEADERS,
        timeout=8)

    if response is None:
        return None

    return response.json()


def change_price(product_id, new_price):
    return api_request("PATCH", f"{PRODUCTS_URL}/{product_id}", json={"price": new_price})


def delete_product(product_id):
    return api_request("DELETE", f"{PRODUCTS_URL}/{product_id}")


def api_request(method, url, **kwargs):
    try:
        return requests.request(method,
                                url,
                                headers=HEADERS,
                                timeout=5,
                                **kwargs)
    except requests.exceptions.RequestException as error:
        print("Could not reach the server:", type(error).__name__)
        return None
