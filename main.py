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
from fastapi import Path, Response

import database
from models import Customer, CustomerInput

load_dotenv()
app = FastAPI()


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
        raise HTTPException(409, "Customer has related records") from error
    if not deleted:
        raise HTTPException(404, "Customer not found")
    return Response(status_code=204)
