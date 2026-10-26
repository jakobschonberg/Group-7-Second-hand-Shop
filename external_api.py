import requests

def get_request(url, params=None, headers=None, timeout=5):
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.Timeout:
        print(f"The request to {url} timed out")
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to the {url} server")
    except requests.exceptions.HTTPError as error:
        print(f"The {url} server said no: {error.response.status_code}")
    except requests.exceptions.JSONDecodeError:
        print(f"The response from {url} was not JSON")
    except requests.exceptions.RequestException as error:
        print(f"Something else went wrong when connecting to {url}: {type(error).__name__}")
    except Exception as error:
        print(error)
    return None

def get_products_from_FakeStoreApi():
    result = get_request("https://fakestoreapi.com/products")
    if type(result) == requests.models.Response and result.status_code == 200:
        return result.json()

def get_categories_from_FakeStoreApi():
    result = get_request("https://fakestoreapi.com/products/categories")
    if type(result) == requests.models.Response and result.status_code == 200:
        return result.json()
