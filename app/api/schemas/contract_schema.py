import re
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator, model_validator

from app.api.schemas.base_schema import BaseSchema, BaseResponseSchema
from app.domain.enums.status import ContractStatus


class ContractBase(BaseSchema):
    contract_number: str = Field(..., min_length=1, max_length=50)
    client_id: int
    price: float = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    start_date: datetime
    end_date: datetime
    payment_terms: Optional[str] = Field(None, max_length=50)
    insurance_coverage: Optional[float] = Field(None, ge=0)
    incoterms: Optional[str] = Field(None, max_length=3)
    status: str = Field(default=ContractStatus.PENDING.value, max_length=20)
    notes: Optional[str] = Field(None, max_length=1023)

    @model_validator(mode="after")
    def end_date_must_be_after_start_date(self) -> "ContractBase":
        if self.end_date < self.start_date:
            raise ValueError("End date must be after start date")
        return self

    @field_validator("status")
    def validate_status(cls, v: str) -> str:
        try:
            return ContractStatus(v).value
        except ValueError:
            valid_statuses = [status.value for status in ContractStatus]
            raise ValueError(f"Status must be one of {valid_statuses}")

    @field_validator("currency")
    def currency_uppercase(cls, v: str) -> str:
        if v != v.upper():
            raise ValueError("Currency must be uppercase (e.g., USD, EUR)")
        return v

    @field_validator("incoterms")
    def validate_incoterms(cls, v: Optional[str]) -> Optional[str]:
        allowed = {"FOB", "CIF", "DAP", "DDP", "EXW"}
        if v is not None and v.upper() not in allowed:
            raise ValueError(f"Incoterms must be one of {allowed}")
        if v is not None and v != v.upper():
            raise ValueError("Incoterms must be uppercase")
        return v

    @field_validator("payment_terms")
    def validate_payment_terms(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.fullmatch(r"\d+\sdays", v.lower()):
            raise ValueError("Payment terms must be like '30 days'")
        return v

    @field_validator("price")
    def validate_price(cls, v: float) -> float:
        if v > 100_000_000:
            raise ValueError("Price seems unrealistic (>100,000,000)")
        return v

    @field_validator("notes")
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() == "":
            raise ValueError("Notes cannot be empty or just spaces")
        return v


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseSchema):
    contract_number: Optional[str] = Field(None, min_length=1, max_length=50)
    client_id: Optional[int] = None
    price: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    payment_terms: Optional[str] = Field(None, max_length=50)
    insurance_coverage: Optional[float] = Field(None, ge=0)
    incoterms: Optional[str] = Field(None, max_length=3)
    status: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = Field(None, max_length=1023)

    @model_validator(mode="before")
    def check_not_empty(cls, data: dict) -> dict:
        if not any(data.values()):
            raise ValueError("At least one field must be updated")
        return data

    @field_validator("status")
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            return ContractStatus(v).value
        except ValueError:
            valid_statuses = [status.value for status in ContractStatus]
            raise ValueError(f"Status must be one of {valid_statuses}")

    @model_validator(mode="after")
    def end_date_must_be_after_start_date(self) -> "ContractUpdate":
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValueError("End date must be after start date")
        return self


class ContractResponse(BaseResponseSchema, ContractBase):
    id: int


class ContractSummary(BaseSchema):
    id: int
    contract_number: str
    client_id: int
    start_date: datetime
    end_date: datetime
    status: str
    price: float
    currency: str
