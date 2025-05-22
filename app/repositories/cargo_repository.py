import logging
from datetime import datetime
from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.domain.enums.status import CargoStatus
from app.domain.models.cargo import Cargo
from app.domain.models.tracking import Tracking
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class CargoRepository(BaseRepository[Cargo]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Cargo)

    async def find_by_contract_id(self, contract_id: int) -> Sequence[Cargo]:
        """
        Fetch cargoes that belong to a specific contract.
        """
        logger.info("Fetching cargoes for contract ID: %s", contract_id)
        stmt = select(Cargo).where(Cargo.contract_id == contract_id)
        result = await self._session.execute(stmt)
        cargoes = result.scalars().all()
        logger.debug("Cargoes found: %d", len(cargoes))
        return cargoes

    async def find_by_status(self, status: CargoStatus) -> Sequence[Cargo]:
        """
        Fetch cargoes with a specific status.
        """
        logger.info("Fetching cargoes with status: %s", status.value)
        stmt = select(Cargo).where(Cargo.status == status.value)
        result = await self._session.execute(stmt)
        cargoes = result.scalars().all()
        logger.debug("Cargoes found with status '%s': %d", status.value, len(cargoes))
        return cargoes

    async def find_by_destination(self, destination: str) -> Sequence[Cargo]:
        """
        Fetch cargoes with destinations that match (case-insensitive, partial match).
        """
        logger.info("Fetching cargoes for destination containing: %s", destination)
        stmt = select(Cargo).where(Cargo.destination.ilike(f"%{destination}%"))
        result = await self._session.execute(stmt)
        cargoes = result.scalars().all()
        logger.debug(
            "Cargoes found for destination '%s': %d", destination, len(cargoes)
        )
        return cargoes

    async def get_by_id_with_tracking(self, cargo_id: int) -> Optional[Cargo]:
        """
        Fetch a cargo by ID and include its tracking records.
        """
        logger.info("Fetching cargo with ID %s including tracking info", cargo_id)
        stmt = (
            select(Cargo)
            .options(joinedload(Cargo.tracking))
            .where(Cargo.id == cargo_id)
        )
        result = await self._session.execute(stmt)
        cargo = result.scalars().first()
        if cargo:
            logger.debug("Cargo with tracking found: ID %s", cargo_id)
        else:
            logger.warning("No cargo found with ID %s", cargo_id)
        return cargo

    async def find_delivered_in_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Cargo]:
        """
        Fetch all delivered cargoes tracked within a given date range.
        """
        logger.info(
            "Fetching delivered cargoes between %s and %s", start_date, end_date
        )
        stmt = (
            select(Cargo)
            .join(Tracking)
            .where(
                Tracking.status == "delivered",
                Tracking.timestamp >= start_date,
                Tracking.timestamp <= end_date,
            )
            .options(joinedload(Cargo.tracking))
        )
        result = await self._session.execute(stmt)
        cargos = result.unique().scalars().all()
        logger.debug("Delivered cargoes in range found: %d", len(cargos))
        return cargos
