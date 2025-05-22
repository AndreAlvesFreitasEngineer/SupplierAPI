from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Float, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.domain.enums.status import VesselStatus
from app.domain.models.base import BaseModel

import logging

# Logger for debugging/logging purposes
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.domain.models.tracking import Tracking


class Vessel(BaseModel):
    """
    Represents a vessel used for transporting cargo.

    Attributes:
        name: Name of the vessel.
        capacity_weight: Maximum weight capacity of the vessel in tons.
        year_built: Year the vessel was constructed.
        status: Operational status (e.g., ACTIVE, MAINTENANCE, RETIRED).
        max_speed: Maximum speed of the vessel in knots.
        current_location: Current geographic or port location of the vessel.
        tracking: Relationship to associated tracking records.
    """

    __tablename__ = "vessel"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity_weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    year_built: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    status: Mapped[VesselStatus] = mapped_column(
        Enum(VesselStatus, native_enum=False, create_constraint=True),
        nullable=False,
        default=VesselStatus.ACTIVE.value,
    )

    max_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_location: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    tracking: Mapped[List["Tracking"]] = relationship(
        "Tracking", back_populates="vessel"
    )

    # Indexes for performance on searchable fields
    __table_args__ = (
        Index("ix_vessel_name", "name"),
        Index("ix_vessel_current_location", "current_location"),
    )

    def __repr__(self) -> str:
        return f"<Vessel(id={self.id}, name={self.name})>"
