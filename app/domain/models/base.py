import logging
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Integer

# Configure logger for this module
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models using declarative mapping."""

    pass


class BaseModel(Base):
    """
    Abstract base class for all database models.
    Adds common fields like `id`, `created_at`, and `updated_at`,
    as well as utility methods for converting to dict and updating fields.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
