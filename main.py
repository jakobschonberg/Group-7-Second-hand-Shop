from fastapi import FastAPI, HTTPException, Query, Path as FastApiPath
from typing import Annotated, Literal
from dotenv import load_dotenv
from pathlib import Path as pathlibPath
from os import getenv, path as osPath
from fastapi import Header, Depends
from json import load, dump

app = FastAPI()

def lowercase(obj):
    if type(obj) is str:
        return obj.lower()
    return obj

@app.get("/products")
def get_products(name: str | None = Query(default=None, min_length=1),
               minimum_price: float | None = Query(default = None),
               maximum_price: float | None = Query(default = None),
               in_stock: bool | None = Query(default = False),
               sort_by: Literal["name", "price", "category"] = "category",
               order: Literal["asc", "desc"] = "asc",
               limit: int = Query(default=10, ge=1, le=100),
               offset: int = Query(default=0, ge=0)):
    rproducts = products
    if name:
        rproducts = [product for product in rproducts if name.lower() in product["name"].lower()]
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