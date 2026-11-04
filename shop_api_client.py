from os import getenv
from dotenv import load_dotenv
from external_api import get_request

load_dotenv()
REST_API_URL = getenv("REST_API_URL", "http://127.0.0.1:8000")
API_KEY = getenv("API_KEY")
PRODUCTS_URL = REST_API_URL + "/products"


def get_products_page(limit: int, offset: int):

    response = get_request(
        PRODUCTS_URL,
        params={"limit": limit, "offset": offset},
        headers={
            "X-API-Key": API_KEY},
        timeout=8)

    if response is None:
        return None

    return response.json()
