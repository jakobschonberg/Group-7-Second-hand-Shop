from fastapi import FastAPI, HTTPException, Query, Path as FastApiPath
from typing import Annotated, Literal
from dotenv import load_dotenv
from pathlib import Path as pathlibPath
from os import getenv, path as osPath
from fastapi import Header, Depends
from json import load, dump
import pprint

app = FastAPI()

from database import imported_products_to_db
from external_api import get_json

base_url = "https://fakestoreapi.com/"

@app.post("/products/", status_code=201) #fetching from products
def seed_products():

    external_products = get_json(base_url + "products")
    pprint.pprint(external_products)
    
    if not external_products:
        raise HTTPException(status_code=503, detail="Error, could not fetch products from external API")
    
    result = imported_products_to_db(external_products)
    
    return {
        "message": "Products imported successfully",
        "imported_new": result["imported"],
        "stock_updated": result["updated"]
    }

seed_products()