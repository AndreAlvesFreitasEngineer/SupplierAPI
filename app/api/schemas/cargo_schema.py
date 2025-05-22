from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator, model_validator

from app.api.schemas.base_schema import BaseSchema, BaseResponseSchema
from app.domain.enums.status import CargoStatus


class CargoBase(BaseSchema):
    contract_id: int
    actual_departure: Optional[datetime] = None
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[str] = Field(None, max_length=50)
    insurance_value: Optional[float] = Field(None, ge=0)
    status: str = Field(default=CargoStatus.PENDING.value, max_length=20)
    cargo_type: Optional[str] = Field(None, max_length=1023)
    destination: Optional[str] = Field(None)

    @field_validator("status")
    def validate_status(cls, v: str) -> str:
        try:
            return CargoStatus(v).value
        except ValueError:
            valid_statuses = [status.value for status in CargoStatus]
            raise ValueError(f"Status must be one of {valid_statuses}")

    @model_validator(mode="after")
    def arrival_after_departure(self) -> "CargoBase":
        if self.actual_arrival and self.actual_departure:
            if self.actual_arrival < self.actual_departure:
                raise ValueError("Actual arrival must be after actual departure")
        return self


class CargoCreate(CargoBase):
    pass


class CargoUpdate(BaseSchema):
    contract_id: Optional[int] = None
    actual_departure: Optional[datetime] = None
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[str] = Field(None, max_length=50)
    insurance_value: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, max_length=20)
    cargo_type: Optional[str] = Field(None, max_length=1023)
    destination: Optional[str] = Field(None)

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
            return CargoStatus(v).value
        except ValueError:
            valid_statuses = [status.value for status in CargoStatus]
            raise ValueError(f"Status must be one of {valid_statuses}")


class CargoResponse(BaseResponseSchema, CargoBase):
    id: int


class CargoSummary(BaseSchema):
    id: int
    contract_id: int
    cargo_type: Optional[str]
    status: str
    destination: Optional[str]
    weight: Optional[float]
