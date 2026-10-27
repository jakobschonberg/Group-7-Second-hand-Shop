from pydantic import BaseModel, Field
from pydantic.types import StringConstraints
from typing import Annotated, Literal
from decimal import Decimal

class Category(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True), Field(min_length=1, max_length=100)]    
    category_id: int = Field(ge=0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Electronics",
                    "category_id": 2
                }
            ]
        }
    }

class Product(BaseModel):
    product_id: int = Field(ge=0)
    name: Annotated[str, StringConstraints(strip_whitespace=True), Field(min_length=1, max_length=100)]    
    price: Decimal = Field(decimal_places=2)
    stock: int = Field(ge=0)
    category_id: int = Field(ge=0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1,
                    "name": "USB-stick 16GB",
                    "price": 119,
                    "stock": 25,
                    "category_id": 2
                }
            ]
        }
    }