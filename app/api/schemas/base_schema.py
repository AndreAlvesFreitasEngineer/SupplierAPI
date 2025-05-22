from datetime import datetime
from typing import Optional, List, Dict, Any, TypeVar, Generic
from pydantic import BaseModel, ConfigDict, model_validator, Field, field_validator


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class BaseResponseSchema(BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int = Field(default=0)

    @model_validator(mode="after")
    def compute_total_pages(cls, values: "PaginatedResponse"):
        values.total_pages = max(
            (values.total + values.page_size - 1) // values.page_size, 1
        )
        return values


class ErrorResponse(BaseSchema):
    detail: str
