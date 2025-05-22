import logging
from datetime import datetime
from typing import Dict, Optional, Any, List, Sequence

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.domain.enums.status import TrackingStatus
from app.domain.models.tracking import Tracking, TrackingHistory
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class TrackingRepository(BaseRepository[Tracking]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Tracking)

    async def find_by_cargo_id(self, cargo_id: int) -> Sequence[Tracking]:
        """
        Fetch all tracking records associated with a given cargo ID.
        """
        logger.info("Fetching tracking entries for cargo_id: %d", cargo_id)
        stmt = select(Tracking).where(Tracking.cargo_id == cargo_id)
        result = await self._session.execute(stmt)
        trackings = result.scalars().all()
        logger.debug("Tracking entries found: %d", len(trackings))
        return trackings

    async def find_by_vessel_id(self, vessel_id: int) -> Sequence[Tracking]:
        """
        Fetch all tracking entries associated with a specific vessel.
        """
        logger.info("Fetching tracking entries for vessel_id: %d", vessel_id)
        stmt = select(Tracking).where(Tracking.vessel_id == vessel_id)
        result = await self._session.execute(stmt)
        trackings = result.scalars().all()
        logger.debug("Tracking entries found: %d", len(trackings))
        return trackings

    async def find_latest_by_cargo_id(self, cargo_id: int) -> Optional[Tracking]:
        """
        Get the most recent tracking record for a specific cargo.
        """
        logger.info("Fetching latest tracking entry for cargo_id: %d", cargo_id)
        stmt = (
            select(Tracking)
            .where(Tracking.cargo_id == cargo_id)
            .order_by(desc(Tracking.timestamp))
        )
        result = await self._session.execute(stmt)
        tracking = result.scalars().first()
        if tracking:
            logger.debug("Latest tracking found with ID: %d", tracking.id)
        else:
            logger.warning("No tracking found for cargo_id: %d", cargo_id)
        return tracking

    async def create_with_history(self, tracking_data: Dict[str, Any]) -> Tracking:
        """
        Create a new tracking record and append it to tracking history.
        """
        logger.info("Creating tracking with historical record")
        try:
            latest_tracking = await self.find_latest_by_cargo_id(
                tracking_data["cargo_id"]
            )
            tracking = await self.create(tracking_data)

            history_data = {
                "tracking_id": tracking.id,
                "cargo_id": tracking.cargo_id,
                "vessel_id": tracking.vessel_id,
                "previous_location": (
                    latest_tracking.location if latest_tracking else None
                ),
                "new_location": tracking.location,
                "previous_status": latest_tracking.status if latest_tracking else None,
                "new_status": tracking.status,
                "changed_at": datetime.utcnow(),
            }

            self._session.add(TrackingHistory(**history_data))
            await self._session.commit()

            logger.debug(
                "Tracking with history created for cargo_id: %d", tracking.cargo_id
            )
            return tracking
        except Exception as e:
            logger.exception("Failed to create tracking with history")
            await self._session.rollback()
            raise e

    async def update_with_history(
        self, tracking_id: int, tracking_data: Dict[str, Any]
    ) -> Optional[Tracking]:
        """
        Update a tracking record and log changes in history if status/location changed.
        """
        logger.info("Updating tracking entry ID: %d with history", tracking_id)
        try:
            tracking = await self.get_by_id(tracking_id)
            if not tracking:
                logger.warning("Tracking ID not found: %d", tracking_id)
                return None

            previous_location = tracking.location
            previous_status = tracking.status

            tracking = await self.update(tracking_id, tracking_data)

            if tracking and (
                previous_location != tracking.location
                or previous_status != tracking.status
            ):
                history_data = {
                    "tracking_id": tracking.id,
                    "cargo_id": tracking.cargo_id,
                    "vessel_id": tracking.vessel_id,
                    "previous_location": previous_location,
                    "new_location": tracking.location,
                    "previous_status": previous_status,
                    "new_status": tracking.status,
                    "changed_at": datetime.utcnow(),
                }

                self._session.add(TrackingHistory(**history_data))
                await self._session.commit()
                logger.debug("Tracking history updated for ID: %d", tracking_id)

            return tracking
        except Exception as e:
            logger.exception("Failed to update tracking with history")
            await self._session.rollback()
            raise e

    async def get_tracking_history(self, cargo_id: int) -> List[TrackingHistory]:
        """
        Retrieve full tracking history for a given cargo.
        """
        logger.info("Fetching tracking history for cargo_id: %d", cargo_id)
        stmt = (
            select(TrackingHistory)
            .where(TrackingHistory.cargo_id == cargo_id)
            .order_by(TrackingHistory.changed_at)
        )
        result = await self._session.execute(stmt)
        history = result.scalars().all()
        logger.debug("Tracking history records found: %d", len(history))
        return history

    async def find_cargoes_by_status(self, status: TrackingStatus) -> List[Tracking]:
        """
        Retrieve all tracking records with a given status and joined cargo data.
        """
        logger.info("Fetching tracking entries by status: %s", status.value)
        stmt = (
            select(Tracking)
            .options(joinedload(Tracking.cargo))
            .where(Tracking.status == status.value)
        )
        result = await self._session.execute(stmt)
        trackings = result.scalars().all()
        logger.debug(
            "Tracking entries with status '%s' found: %d", status.value, len(trackings)
        )
        return trackings
