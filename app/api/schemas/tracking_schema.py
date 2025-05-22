from datetime import datetime
from typing import Optional
from pydantic import Field, field_validator
from app.api.schemas.base_schema import BaseSchema
from app.domain.enums.status import TrackingStatus
from pydantic import ConfigDict


class TrackingBase(BaseSchema):
    status: str = Field(
        ..., description="Tracking status (e.g., loading, in_transit, delivered)"
    )

    @field_validator("status")
    def validate_status(cls, v):
        allowed = {item.value for item in TrackingStatus}
        if v not in allowed:
            raise ValueError(f"Status '{v}' is not allowed. Must be one of: {allowed}")
        return v


class TrackingCreate(TrackingBase):
    cargo_id: int = Field(..., gt=0)
    vessel_id: int = Field(..., gt=0)
    location: Optional[str] = Field(None, max_length=100)
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = Field(None, max_length=511)
    temperature: Optional[float] = None


class TrackingUpdate(TrackingBase):
    status: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    timestamp: Optional[datetime]
    notes: Optional[str]
    temperature: Optional[float]


class TrackingResponse(TrackingCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrackingHistoryResponse(BaseSchema):
    id: int
    tracking_id: int
    cargo_id: int
    vessel_id: int
    previous_status: Optional[str]
    new_status: str
    previous_location: Optional[str]
    new_location: str
    timestamp: datetime
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
