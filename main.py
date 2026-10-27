from fastapi import FastAPI, HTTPException, Query, Path as FastApiPath
from typing import Annotated, Literal
from dotenv import load_dotenv
from pathlib import Path as pathlibPath
from os import getenv, path as osPath
from fastapi import Header, Depends
from json import load, dump
from models import Product, Category

app = FastAPI()

def lowercase(obj):
    if type(obj) is str:
        return obj.lower()
    return obj

def get_categories_from_database():
    #TODO: remove this placeholder function
    categories = [{"name": "Clothings", "category_id": 1},
        {"name": "Electronics", "category_id": 2}]
    return categories

def get_products_from_database():
    #TODO: remove this placeholder function
    products = [{"product_id": 2, "name": "T-shirt, white", "price": 99.99, "stock": 25, "category_id":1},
        {"product_id": 1, "name": "USB stick 16 GB", "price": 119, "stock": 22, "category_id":2}]
    return products

categories = get_categories_from_database()
products = get_products_from_database()
print(products)
print(categories)

@app.get("/products")
def get_products(name: str | None = Query(default=None, min_length=2),
    category: str | None = Query(default=None, min_length=2),
    minimum_price: float | None = Query(default = None),
    maximum_price: float | None = Query(default = None),
    in_stock: bool | None = Query(default = False),
    sort_by: Literal["name", "price", "category"] = "name",
    order: Literal["asc", "desc"] = "asc",
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0)):
    rproducts = products
    if name:
        rproducts = [product for product in rproducts if name.lower() in product["name"].lower()]
    if category:
        matching_categories = [cat for cat in categories if category.lower() in cat["name"].lower()]
        rproducts = [product for product in rproducts if product["category_id"] in map(lambda d: d["category_id"], matching_categories)]
    if minimum_price:
        rproducts = [product for product in rproducts if product["price"] >= minimum_price]
    if maximum_price:
        rproducts = [product for product in rproducts if product["price"] <= maximum_price]
    if in_stock:
        rproducts = [product for product in rproducts if product["stock"] >= 1]
    sorted_products = sorted(rproducts, key=lambda m: lowercase(m[sort_by]), reverse=(order == "desc"))
    total = len(sorted_products)
    page = sorted_products[offset:offset + limit]
    return {"total": total, "limit": limit, "offset": offset, "products": page}


@app.get("/products/{product_id}")
def get_product(product_id: int = FastApiPath(ge=0)):
    found_product = next((product for product in products if product["id"] == product_id), None)
    if found_product:
        return found_product
    raise HTTPException(status_code=404, detail="product not found")

