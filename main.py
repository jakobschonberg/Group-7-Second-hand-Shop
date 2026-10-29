import os
import secrets
import sqlite3

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Path as FastApiPath
from typing import Annotated, Literal
from pathlib import Path as pathlibPath
from os import getenv, path as osPath
from fastapi import Header, Depends
from json import load, dump
import pprint
from models import Product, Category
from functools import cmp_to_key
from fastapi import Path, Response

import database
from models import Customer, CustomerInput

load_dotenv()
app = FastAPI()

def lowercase(obj):
    if type(obj) is str:
        return obj.lower()
    return obj

def get_categories_from_database():
    #TODO: remove this placeholder function
    categories = [{"name": "Clothings", "category_id": 1},
        {"name": "Electronics", "category_id": 2},
        {"name": "Shoes", "category_id": 3}]
    return categories

def get_products_from_database():
    #TODO: remove this placeholder function
    products = [{"product_id": 2, "name": "T-shirt, white", "price": 99.99, "stock": 25, "category_id":1},
        {"product_id": 3, "name": "Sneakers, size: 49", "price": 1300, "stock": 1, "category_id": 3},
        {"product_id": 1, "name": "USB stick 16 GB", "price": 119, "stock": 0, "category_id":2}]
    for product in products:
        product_category = next(cat for cat in categories if product["category_id"] == cat["category_id"])
        product["category_name"] = product_category["name"]
    return products

categories = get_categories_from_database()
products = get_products_from_database()


def products_compared_by_category(x: dict, y: dict):
    x_category = next((category for category in categories if x["category_id"] == category["category_id"]), None)
    y_category = next((category for category in categories if y["category_id"] == category["category_id"]), None)
    print(x_category["name"], y_category["name"], x_category["name"] < y_category["name"])
    if x_category["name"] < y_category["name"]:
        return -1
    if x_category["name"] > y_category["name"]:
        return 1
    return 0

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
    sorted_products = []
    if sort_by == "category":
        sorted_products = sorted(rproducts, key=cmp_to_key(products_compared_by_category), reverse=(order == "desc"))
    else:
        sorted_products = sorted(rproducts, key=lambda m: lowercase(m[sort_by]), reverse=(order == "desc"))
    total = len(sorted_products)
    page = sorted_products[offset:offset + limit]
    return {"total": total, "limit": limit, "offset": offset, "products": page}


@app.get("/products/{product_id}")
def get_product(product_id: int = FastApiPath(ge=0)):
    found_product = next((product for product in products if product["product_id"] == product_id), None)
    if found_product:
        return found_product
    raise HTTPException(status_code=404, detail="product not found")


def require_api_key(x_api_key: str | None = Header(default=None)):
    expected = os.getenv("API_KEY")
    if not expected or not x_api_key or not secrets.compare_digest(
        expected.encode(), x_api_key.encode()
    ):
        raise HTTPException(401, "Invalid or missing API key")


@app.get("/customers", response_model=list[Customer])
def get_customers():
    return database.list_customers()


@app.post("/customers", response_model=Customer, status_code=201,
          dependencies=[Depends(require_api_key)])
def post_customer(customer: CustomerInput):
    try:
        return database.create_customer(customer.model_dump())
    except sqlite3.IntegrityError as error:
        raise HTTPException(409, "Customer data conflict") from error


@app.put("/customers/{customer_id}", response_model=Customer,
         dependencies=[Depends(require_api_key)])
def put_customer(customer: CustomerInput, customer_id: int = Path(gt=0)):
    try:
        result = database.update_customer(customer_id, customer.model_dump())
    except sqlite3.IntegrityError as error:
        raise HTTPException(409, "Customer data conflict") from error
    if result is None:
        raise HTTPException(404, "Customer not found")
    return result


@app.delete("/customers/{customer_id}", status_code=204,
            dependencies=[Depends(require_api_key)])
def remove_customer(customer_id: int = Path(gt=0)):
    try:
        deleted = database.delete_customer(customer_id)
    except (ValueError, sqlite3.IntegrityError) as error:
        raise HTTPException(
            409, "Cannot delete customer because related records exist"
        ) from error
    if not deleted:
        raise HTTPException(404, "Customer not found")
    return Response(status_code=204)
