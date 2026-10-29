from fastapi import FastAPI, HTTPException, Header, Depends
from dotenv import load_dotenv
import os
import database
import sqlite3
from models import CreateProduct, UpdateProduct

load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API KEY is not configured or empty")
app = FastAPI()


def check_auth(x_api_key: str | None = Header(default=None)):
    if not API_KEY:
        print("API_KEY is not configured or empty")
        raise HTTPException(status_code=500)
    if not x_api_key or not x_api_key.strip():
        raise HTTPException(status_code=401, detail="Api key is not provided")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401)


@app.post("/products", dependencies=[Depends(check_auth)], status_code=201)
def create_products(product: CreateProduct):
    new_product = {
        "name": product.name,
        "category_id": product.category_id,
        "price": product.price,
        "stock": product.stock
    }
    try:
        new_product_id = database.create_product(new_product)
        return {"product_id": new_product_id, **new_product}
    except sqlite3.IntegrityError as error:
        print(error)
        if "FOREIGN KEY" in str(error):
            raise HTTPException(
                status_code=422, detail="Category does not exist") from error
        if "UNIQUE" in str(error):
            raise HTTPException(
                status_code=409, detail="Product Already exists") from error
        raise HTTPException(
            status_code=422) from error


@app.patch("/products/{product_id}", dependencies=[Depends(check_auth)])
def update_product(changes: UpdateProduct, product_id: int):
    try:
        existing_product = database.search_product(product_id)
        if existing_product is None:
            raise HTTPException(status_code=404, detail="Product Not Found")

        existing_product.update(changes.model_dump(exclude_unset=True))
        if not database.update_product(product_id, existing_product):
            raise HTTPException(status_code=404, detail="Product Not Found")
        return existing_product

    except sqlite3.IntegrityError as error:
        if "FOREIGN KEY" in str(error):
            raise HTTPException(
                status_code=422, detail="Category does not exist") from error
        raise HTTPException(
            status_code=422) from error


@app.delete("/products/{product_id}", dependencies=[Depends(check_auth)], status_code=204)
def delete_product(product_id: int):
    try:
        if not database.delete_product(product_id):
            raise HTTPException(status_code=404, detail="Product not found")

    except sqlite3.IntegrityError as error:
        raise HTTPException(
            status_code=409, detail="Cannot delete product because related records exist") from error
