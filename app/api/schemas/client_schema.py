import re
from typing import Optional, List

from pydantic import EmailStr, Field, model_validator, constr, field_validator

from app.api.schemas.base_schema import (
    BaseSchema,
    BaseResponseSchema,
    PaginatedResponse,
)
from app.domain.models.base import BaseModel


class ClientBase(BaseSchema):
    company_name: str = Field(..., min_length=1, max_length=255)
    contact_email: EmailStr
    contact_phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=511)
    tax_id: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    active: bool = True
    credit_limit: Optional[float] = Field(None, ge=0)
    payment_terms: Optional[str] = Field(None, max_length=50)


class ClientCreate(BaseSchema):
    company_name: constr(strip_whitespace=True, min_length=1, max_length=255)
    contact_email: EmailStr
    contact_phone: constr(strip_whitespace=True, min_length=8, max_length=20) = None
    tax_id: constr(strip_whitespace=True, min_length=9, max_length=15) = None
    address: constr(strip_whitespace=True, max_length=255) = None
    credit_limit: float = 0
    industry: str = None
    payment_terms: str = None
    active: bool = True

    @field_validator("credit_limit")
    def credit_limit_non_negative_and_reasonable(cls, v):
        if v < 0:
            raise ValueError("Credit limit must be non-negative")
        if v > 10_000_000:
            raise ValueError("Credit limit too high (max 10,000,000)")
        return v

    @field_validator("contact_phone")
    def phone_digits_only(cls, v):
        if v and not re.fullmatch(r"\d+", v):
            raise ValueError("Contact phone must contain only digits")
        return v

    @field_validator("tax_id")
    def tax_id_format(cls, v):
        if v and not re.fullmatch(r"\d{9}", v):
            raise ValueError("Tax ID (NIF) must have 9 digits")
        return v

    @field_validator("company_name")
    def company_name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Company name cannot be empty or just spaces")
        return v

    @field_validator("payment_terms")
    def validate_payment_terms(cls, v):
        if v and not re.fullmatch(r"\d+\s*days", v.lower()):
            raise ValueError("Payment terms must be like '30 days'")
        return v


class ClientUpdate(BaseSchema):
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=511)
    tax_id: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    active: Optional[bool] = None
    credit_limit: Optional[float] = Field(None, ge=0)
    payment_terms: Optional[str] = Field(None, max_length=50)

    @model_validator(mode="before")
    def check_not_empty(cls, data: dict) -> dict:
        if not any(data.values()):
            raise ValueError("At least one field must be updated")
        return data


class ClientResponse(BaseResponseSchema, ClientBase):
    id: int


class ClientSummary(BaseSchema):
    id: int
    company_name: str
    contact_email: EmailStr
    active: bool


class PaginatedClientSummaryResponse(PaginatedResponse[ClientSummary]):
    items: List[ClientSummary]
