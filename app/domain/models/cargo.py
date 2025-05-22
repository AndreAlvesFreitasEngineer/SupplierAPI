from __future__ import annotations
import logging
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import (
    String,
    Float,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums.status import CargoStatus
from app.domain.models.base import BaseModel

# Only import related models for type checking to avoid circular imports at runtime
if TYPE_CHECKING:
    from app.domain.models.contract import Contract
    from app.domain.models.tracking import Tracking

# Logger setup
logger = logging.getLogger(__name__)


class Cargo(BaseModel):
    """
    ORM model for cargo records in the shipping system.

    Attributes:
        contract_id: FK to the related contract.
        actual_departure: Actual departure datetime (nullable).
        estimated_arrival: Estimated arrival datetime (nullable).
        actual_arrival: Actual arrival datetime (nullable).
        weight: Weight of the cargo in kg or tons.
        dimensions: Physical dimensions as string.
        insurance_value: Insured monetary value.
        status: Cargo status (Pending, In Transit, Delivered).
        cargo_type: Description or classification of the cargo.
        destination: Final destination.
    """

    __tablename__ = "cargo"

    contract_id: Mapped[int] = mapped_column(ForeignKey("contract.id"), nullable=False)
    actual_departure: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    estimated_arrival: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    actual_arrival: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dimensions: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    insurance_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=CargoStatus.PENDING.value
    )
    cargo_type: Mapped[Optional[str]] = mapped_column(String(1023), nullable=True)
    destination: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    contract: Mapped["Contract"] = relationship("Contract", back_populates="cargoes")
    tracking: Mapped[List["Tracking"]] = relationship(
        "Tracking", back_populates="cargo", cascade="all, delete-orphan"
    )

    # Indexes for performance
    __table_args__ = (
        Index("ix_cargo_status", "status"),
        Index("ix_cargo_destination", "destination"),
    )

    def __repr__(self) -> str:
        """
        String representation for debugging and logging.
        """
        return (
            f"<Cargo(id={self.id}, type='{self.cargo_type}', "
            f"status='{self.status}', destination='{self.destination}')>"
        )
