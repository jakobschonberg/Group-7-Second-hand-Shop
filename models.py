from pydantic import BaseModel, Field, StringConstraints
from pydantic import ConfigDict, EmailStr
from typing import Annotated
from pydantic import BaseModel, Field
from pydantic.types import StringConstraints
from typing import Annotated, Literal
from decimal import Decimal


class Category(BaseModel):
    name: Annotated[str, StringConstraints(
        strip_whitespace=True), Field(min_length=1, max_length=100)]
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
    name: Annotated[str, StringConstraints(
        strip_whitespace=True), Field(min_length=1, max_length=100)]
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


class CustomerInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone_no: str | None = Field(default=None, max_length=50)
    city: str | None = Field(default=None, max_length=100)


class Customer(CustomerInput):
    customer_id: int


class CreateProduct(BaseModel):
    name: Annotated[str, StringConstraints(
        strip_whitespace=True, min_length=1, max_length=100)]
    category_id: int = Field(ge=1)
    price: float = Field(ge=0, allow_inf_nan=False)
    stock: int = Field(ge=0)


class UpdateProduct(BaseModel):
    name: Annotated[str, StringConstraints(
        strip_whitespace=True, min_length=1, max_length=100)] | None = None
    category_id: int | None = Field(default=None, ge=1)
    price: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    stock: int | None = Field(default=None, ge=0)


class OrderItemInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_id: int = Field(gt=0, strict=True)
    quantity: int = Field(gt=0, strict=True)


class OrderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: int = Field(gt=0, strict=True)
    items: list[OrderItemInput] = Field(min_length=1)


class OrderStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["NEW", "DELIVERED", "CANCELLED"]
