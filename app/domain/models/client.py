from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import String, Float, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel

if TYPE_CHECKING:
    from app.domain.models.contract import Contract

# Logger for debugging or exception logging
logger = logging.getLogger(__name__)


class Client(BaseModel):
    """
    ORM model representing a client entity.

    Attributes:
        company_name: Name of the company (required).
        contact_email: Primary email address (required).
        contact_phone: Optional contact phone number.
        address: Optional physical address.
        tax_id: Unique tax identification number (optional, must be unique).
        industry: Optional industry or sector description.
        active: Indicates if the client is active in the system.
        credit_limit: Credit limit assigned to the client (must be non-negative).
        payment_terms: Optional payment terms string (e.g., "30 days").
        contracts: List of contracts associated with the client.
    """

    __tablename__ = "client"

    # Ensure credit_limit is non-negative
    __table_args__ = (
        CheckConstraint(
            "credit_limit >= 0", name="ck_client_credit_limit_non_negative"
        ),
    )

    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(511), nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, nullable=True
    )
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    credit_limit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    payment_terms: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # One-to-many relationship with contracts
    contracts: Mapped[List["Contract"]] = relationship(
        "Contract", back_populates="client", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """
        String representation for debugging/logging.
        """
        return f"<Client(id={self.id}, company={self.company_name!r})>"
