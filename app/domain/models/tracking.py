from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime, Enum, String, Float, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums.status import TrackingStatus
from app.domain.models.base import BaseModel

import logging

from app.domain.models.cargo import Cargo
from app.domain.models.vessel import Vessel

# Logger instance for debugging/tracing
logger = logging.getLogger(__name__)


class Tracking(BaseModel):
    """
    Represents the current state of cargo being tracked.

    Attributes:
        cargo_id: Foreign key to the cargo being tracked.
        vessel_id: Foreign key to the vessel carrying the cargo.
        status: Current status of the cargo (e.g., LOADING, IN_TRANSIT, DELIVERED).
        location: Current or last known location of the cargo.
        timestamp: Date and time the tracking entry was recorded.
        notes: Optional textual notes for the entry.
        temperature: Optional cargo temperature reading.
        cargo: SQLAlchemy relationship to the Cargo entity.
        vessel: SQLAlchemy relationship to the Vessel entity.
        history_records: Related history entries tracking changes over time.
    """

    __tablename__ = "tracking"

    cargo_id: Mapped[int] = mapped_column(ForeignKey("cargo.id"), nullable=False)
    vessel_id: Mapped[int] = mapped_column(ForeignKey("vessel.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TrackingStatus.LOADING.value
    )
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    notes: Mapped[Optional[str]] = mapped_column(String(511), nullable=True)
    temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    cargo: Mapped["Cargo"] = relationship("Cargo", back_populates="tracking")
    vessel: Mapped["Vessel"] = relationship("Vessel", back_populates="tracking")
    history_records: Mapped[List["TrackingHistory"]] = relationship(
        "TrackingHistory", back_populates="tracking", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_tracking_cargo_id", "cargo_id"),
        Index("ix_tracking_location", "location"),
        Index("ix_tracking_status", "status"),
    )

    def __repr__(self) -> str:
        return (
            f"<Tracking(id={self.id}, cargo_id={self.cargo_id}, "
            f"location='{self.location}', status='{self.status}')>"
        )


class TrackingHistory(BaseModel):
    """
    Logs historical changes to a tracking record.

    Attributes:
        tracking_id: Foreign key to the associated tracking entry.
        cargo_id: Redundant foreign key for easier querying.
        vessel_id: Redundant foreign key for vessel.
        previous_location: Where the cargo was before this event.
        new_location: Updated location of the cargo.
        previous_status: Status before the change.
        new_status: Updated status.
        changed_at: Timestamp when the change occurred.
        tracking: Back-reference to the tracking entity.
    """

    __tablename__ = "tracking_history"

    tracking_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tracking.id"), nullable=False
    )
    cargo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cargo.id"), nullable=False
    )
    vessel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vessel.id"), nullable=False
    )

    previous_location = mapped_column(String, nullable=True)
    new_location: Mapped[str] = mapped_column(String(100), nullable=True)
    previous_status = mapped_column(String, nullable=True)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationship
    tracking: Mapped["Tracking"] = relationship(
        "Tracking", back_populates="history_records"
    )

    __table_args__ = (
        Index("ix_tracking_history_cargo_id", "cargo_id"),
        Index("ix_tracking_history_tracking_id", "tracking_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<TrackingHistory(id={self.id}, cargo_id={self.cargo_id}, "
            f"changed_at='{self.changed_at}')>"
        )
