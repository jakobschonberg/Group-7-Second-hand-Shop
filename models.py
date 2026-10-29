from pydantic import BaseModel, Field
from pydantic.types import StringConstraints
from pydantic import ConfigDict, EmailStr


class CustomerInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone_no: str | None = Field(default=None, max_length=50)
    city: str | None = Field(default=None, max_length=100)


class Customer(CustomerInput):
    customer_id: int
