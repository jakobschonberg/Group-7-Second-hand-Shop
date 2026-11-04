from os import getenv
from typing import Literal
from secrets import compare_digest
from sqlite3 import IntegrityError, Error
from fastapi import FastAPI, HTTPException, Header, Depends, Query, Path as FastApiPath
from models import OrderInput, OrderStatusUpdate
from dotenv import load_dotenv
import database
from models import Customer, CustomerInput, CreateProduct, UpdateProduct, CategoryRevenue
from receipt import Receipt_row, Receipt


load_dotenv()
app = FastAPI()


def lowercase(obj):
    if type(obj) is str:
        return obj.lower()
    return obj


def products_with_category_names(categories) -> list[dict]:
    products = database.get_all_products_from_db()
    for product in products:
        product_category = next(
            (cat for cat in categories if product["category_id"] == cat["category_id"]), None)
        if product_category:
            product["category_name"] = product_category["name"]
        else:
            product["category_name"] = "(unknown)"
    return products


@app.get("/products")
def get_products(name: str | None = Query(default=None, min_length=2),
                 category: str | None = Query(default=None, min_length=2),
                 minimum_price: float | None = Query(default=None),
                 maximum_price: float | None = Query(default=None),
                 in_stock: bool | None = Query(default=False),
                 sort_by: Literal["name", "price", "category_name"] = "name",
                 order: Literal["asc", "desc"] = "asc",
                 limit: int = Query(default=100, ge=1, le=100),
                 offset: int = Query(default=0, ge=0)):

    categories = database.get_all_categories_from_db()
    products = products_with_category_names(categories)

    rproducts = products
    if name:
        rproducts = [product for product in rproducts if name.lower()
                     in product["name"].lower()]
    if category:
        matching_categories = [
            cat for cat in categories if category.lower() in cat["name"].lower()]
        rproducts = [product for product in rproducts if product["category_id"] in map(
            lambda d: d["category_id"], matching_categories)]
    if minimum_price:
        rproducts = [
            product for product in rproducts if product["price"] >= minimum_price]
    if maximum_price:
        rproducts = [
            product for product in rproducts if product["price"] <= maximum_price]
    if in_stock:
        rproducts = [product for product in rproducts if product["stock"] >= 1]
    sorted_products = sorted(rproducts, key=lambda m: lowercase(
        m[sort_by]), reverse=(order == "desc"))
    total = len(sorted_products)
    page = sorted_products[offset:offset + limit]
    return {"total": total, "limit": limit, "offset": offset, "products": page}


@app.get("/products/{product_id}")
def get_product(product_id: int = FastApiPath(ge=0)):
    categories = database.get_all_categories_from_db()
    products = products_with_category_names(categories)
    found_product = next(
        (product for product in products if product["product_id"] == product_id), None)
    if found_product:
        return found_product
    raise HTTPException(status_code=404, detail="product not found")


def require_api_key(x_api_key: str | None = Header(default=None)):
    expected = getenv("API_KEY")
    if not expected or not x_api_key or not compare_digest(
        expected.encode(), x_api_key.encode()
    ):
        raise HTTPException(401, "Invalid or missing API key")


@app.get("/customers", response_model=list[Customer], dependencies=[Depends(require_api_key)])
def get_customers():
    return database.list_customers()


@app.post("/customers", response_model=Customer, status_code=201,
          dependencies=[Depends(require_api_key)])
def post_customer(customer: CustomerInput):
    try:
        return database.create_customer(customer.model_dump())
    except IntegrityError as error:
        raise HTTPException(409, "Customer data conflict") from error


@app.put("/customers/{customer_id}", response_model=Customer,
         dependencies=[Depends(require_api_key)])
def put_customer(customer: CustomerInput, customer_id: int = FastApiPath(gt=0)):
    try:
        result = database.update_customer(customer_id, customer.model_dump())
    except IntegrityError as error:
        raise HTTPException(409, "Customer data conflict") from error
    if result is None:
        raise HTTPException(404, "Customer not found")
    return result


@app.delete("/customers/{customer_id}", status_code=200,
            dependencies=[Depends(require_api_key)])
def remove_customer(customer_id: int = FastApiPath(gt=0)):
    action = database.delete_customer(customer_id)

    if action == False:
        raise HTTPException(status_code=404, detail="Customer not found")

    if action == "pseudonymized":
        return {"message": "Customer has orders within the last seven years and was thus pseudonymized instead of deleted."}
    else:
        return {"message": "Customer had no orders within the last seven years and was permanently deleted."}


@app.post("/products", dependencies=[Depends(require_api_key)], status_code=201)
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
    except IntegrityError as error:
        print(error)
        if "FOREIGN KEY" in str(error):
            raise HTTPException(
                status_code=422, detail="Category does not exist") from error
        if "UNIQUE" in str(error):
            raise HTTPException(
                status_code=409, detail="Product Already exists") from error
        raise HTTPException(
            status_code=422) from error


@app.patch("/products/{product_id}", dependencies=[Depends(require_api_key)])
def update_product(changes: UpdateProduct, product_id: int):
    try:
        existing_product = database.search_product(product_id)
        if existing_product is None:
            raise HTTPException(status_code=404, detail="Product Not Found")

        existing_product.update(changes.model_dump(exclude_unset=True))
        if not database.update_product(product_id, existing_product):
            raise HTTPException(status_code=404, detail="Product Not Found")
        return existing_product

    except IntegrityError as error:
        if "FOREIGN KEY" in str(error):
            raise HTTPException(
                status_code=422, detail="Category does not exist") from error
        raise HTTPException(
            status_code=422) from error


@app.delete("/products/{product_id}", dependencies=[Depends(require_api_key)], status_code=204)
def delete_product(product_id: int):
    try:
        if not database.delete_product(product_id):
            raise HTTPException(status_code=404, detail="Product not found")

    except IntegrityError as error:
        raise HTTPException(
            status_code=409, detail="Cannot delete product because related records exist") from error


@app.get("/orders/{order_id}/receipt", dependencies=[Depends(require_api_key)])
def get_receipt(order_id: int = FastApiPath(ge=0)):
    receipt_rows = database.get_receipt_from_db(order_id)
    if len(receipt_rows) == 0:
        raise HTTPException(status_code=404, detail="order not found")
    row0 = receipt_rows[0]
    receipt = Receipt(row0["order_date"], row0["order_id"], [])
    for row in receipt_rows:
        receipt.add_row(Receipt_row(
            row["name"], row["quantity"], row["unit_price"], row["row_price"]))
    return receipt


@app.get("/orders", dependencies=[Depends(require_api_key)])
def get_orders(customer_id: int | None = Query(default=None, gt=0)):
    try:
        return database.list_orders(customer_id)
    except LookupError as error:
        raise HTTPException(404, str(error)) from error


@app.get("/orders/{order_id}", dependencies=[Depends(require_api_key)])
def get_order(order_id: int = FastApiPath(gt=0)):
    order = database.get_order(order_id)
    if order is None:
        raise HTTPException(404, "Order not found")
    return order


@app.post("/orders", status_code=201,
          dependencies=[Depends(require_api_key)])
def post_order(order: OrderInput):
    try:
        return database.create_order(order.model_dump())
    except LookupError as error:
        raise HTTPException(404, str(error)) from error
    except ValueError as error:
        raise HTTPException(409, str(error)) from error


@app.patch("/orders/{order_id}", dependencies=[Depends(require_api_key)])
def patch_order(changes: OrderStatusUpdate, order_id: int = FastApiPath(gt=0)):
    try:
        return database.update_order_status(order_id, changes.status)
    except LookupError as error:
        raise HTTPException(404, str(error)) from error
    except ValueError as error:
        raise HTTPException(409, str(error)) from error




@app.get("/reports/revenue", dependencies=[Depends(require_api_key)], response_model=list[CategoryRevenue])
def get_revenue():
    try:
        return database.get_revenue_per_category()
    except Error as error:
        raise HTTPException(
            status_code=500, detail="Could not read revenue data") from error
