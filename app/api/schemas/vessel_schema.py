from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator, model_validator

from app.api.schemas.base_schema import BaseSchema, BaseResponseSchema
from app.domain.enums.status import VesselStatus


class VesselBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    capacity_weight: Optional[float] = Field(None, gt=0)
    year_built: Optional[int] = Field(None, ge=1900, le=2100)
    status: str = Field(default=VesselStatus.ACTIVE.value, max_length=20)
    max_speed: Optional[float] = Field(None, gt=0)
    current_location: str = Field(..., min_length=1, max_length=50)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        try:
            return VesselStatus(v).value
        except ValueError:
            valid_statuses = [status.value for status in VesselStatus]
            raise ValueError(f"Status must be one of {valid_statuses}")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be blank or just spaces")
        return v

    @field_validator("current_location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Current location cannot be blank or just spaces")
        return v

    @field_validator("year_built")
    @classmethod
    def validate_year_built(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            this_year = datetime.now().year
            if v > this_year + 2:
                raise ValueError(
                    f"Year built cannot be in the distant future ({this_year+2})"
                )
        return v


class VesselCreate(VesselBase):
    pass


class VesselUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    capacity_weight: Optional[float] = Field(None, gt=0)
    year_built: Optional[int] = Field(None, ge=1900, le=2100)
    status: Optional[str] = Field(None, max_length=20)
    max_speed: Optional[float] = Field(None, gt=0)
    current_location: Optional[str] = Field(None, min_length=1, max_length=50)

    @classmethod
    def check_not_empty(cls, data: dict) -> dict:
        if not any(data.values()):
            raise ValueError("At least one field must be updated")
        return data

    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            return VesselStatus(v).value
        except ValueError:
            valid_statuses = [status.value for status in VesselStatus]
            raise ValueError(f"Status must be one of {valid_statuses}")


class VesselResponse(BaseResponseSchema, VesselBase):
    id: int


class VesselSummary(BaseSchema):
    id: int
    name: str
    capacity_weight: Optional[float]
    status: str
    current_location: str
