import logging
from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums.status import VesselStatus
from app.domain.models.vessel import Vessel
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class VesselRepository(BaseRepository[Vessel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Vessel)

    async def find_by_name(self, name: str) -> Optional[Vessel]:
        """
        Retrieve a vessel by its exact name.
        """
        logger.info("Searching for vessel with name: %s", name)
        stmt = select(Vessel).where(Vessel.name == name)
        result = await self._session.execute(stmt)
        vessel = result.scalar_one_or_none()

        if vessel:
            logger.debug("Vessel found: %s (ID: %d)", vessel.name, vessel.id)
        else:
            logger.warning("No vessel found with name: %s", name)

        return vessel

    async def find_by_status(self, status: VesselStatus) -> Sequence[Vessel]:
        """
        Retrieve all vessels matching the given status.
        """
        logger.info("Fetching vessels with status: %s", status.value)
        stmt = select(Vessel).where(Vessel.status == status.value)
        result = await self._session.execute(stmt)
        vessels = result.scalars().all()
        logger.debug("Vessels found with status '%s': %d", status.value, len(vessels))
        return vessels

    async def find_available_vessels(self, min_capacity: float = 0) -> Sequence[Vessel]:
        """
        Retrieve vessels with 'ACTIVE' status and at least the given capacity.
        """
        logger.info(
            "Fetching available vessels with minimum capacity: %.2f", min_capacity
        )
        stmt = select(Vessel).where(
            Vessel.status == VesselStatus.ACTIVE.value,
            Vessel.capacity_weight >= min_capacity,
        )
        result = await self._session.execute(stmt)
        vessels = result.scalars().all()
        logger.debug("Available vessels found: %d", len(vessels))
        return vessels

    async def find_by_location(self, location: str) -> Sequence[Vessel]:
        """
        Retrieve all vessels currently located in a specific place (partial match, case-insensitive).
        """
        logger.info("Searching for vessels in location like: %s", location)
        stmt = select(Vessel).where(Vessel.current_location.ilike(f"%{location}%"))
        result = await self._session.execute(stmt)
        vessels = result.scalars().all()
        logger.debug("Vessels found in location '%s': %d", location, len(vessels))
        return vessels
