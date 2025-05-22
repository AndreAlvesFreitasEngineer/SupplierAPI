from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.domain.enums.status import ContractStatus
from app.domain.models.base import BaseModel

import logging

if TYPE_CHECKING:
    from app.domain.models.cargo import Cargo
    from app.domain.models.client import Client

# Logger for debugging or exception logging
logger = logging.getLogger(__name__)


class Contract(BaseModel):
    """
    ORM model representing a service contract between a client and the company.

    Attributes:
        contract_number (str): Unique identifier of the contract.
        client_id (int): Foreign key referencing the client.
        price (float): Agreed price for the contract.
        currency (str): Currency code (e.g., USD, EUR).
        start_date (datetime): Start date of the contract.
        end_date (datetime): End date of the contract.
        payment_terms (Optional[str]): Terms of payment (e.g., '30 days').
        insurance_coverage (Optional[float]): Optional insurance amount.
        incoterms (Optional[str]): International commercial terms code.
        status (str): Current status of the contract.
        notes (Optional[str]): Additional notes related to the contract.
        client (Client): Relationship to the Client entity.
        cargoes (List[Cargo]): List of cargoes associated with this contract.
    """

    __tablename__ = "contract"

    # Columns
    contract_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    payment_terms: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    insurance_coverage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    incoterms: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ContractStatus.PENDING.value
    )
    notes: Mapped[Optional[str]] = mapped_column(String(1023), nullable=True)

    # Relationships
    client: Mapped["Client"] = relationship("Client", back_populates="contracts")
    cargoes: Mapped[List["Cargo"]] = relationship(
        "Cargo", back_populates="contract", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_contract_client_id", "client_id"),)

    def __repr__(self) -> str:
        """
        String representation for debugging/logging purposes.
        """
        return f"<Contract(id={self.id}, number={self.contract_number!r})>"
