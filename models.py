from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated


class CreateProduct(BaseModel):
    name: Annotated[str, StringConstraints(
        strip_whitespace=True, min_length=1, max_length=100)]
    category_id: int = Field(ge=1)
    price: float = Field(ge=0, allow_inf_nan=False)
    stock: int = Field(ge=0)


class UpdateProduct(BaseModel):
    name: Annotated[str, StringConstraints(
        strip_whitespace=True, min_length=1, max_length=100)]
    category_id: int | None = Field(default=None, ge=1)
    price: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    stock: int | None = Field(default=None, ge=0)


class Product(BaseModel):
    product_id: int
    name: str
    category_id: int
    price: float
    stock: int
