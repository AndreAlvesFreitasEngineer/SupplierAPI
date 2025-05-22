import logging
from typing import List, Optional

from app.repositories.tracking_repository import TrackingRepository
from app.domain.enums.status import TrackingStatus
from app.api.schemas.tracking_schema import (
    TrackingCreate,
    TrackingUpdate,
    TrackingResponse,
    TrackingHistoryResponse,
)
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class TrackingService(BaseService[TrackingResponse]):
    def __init__(self, repository: TrackingRepository):
        super().__init__(repository, response_schema=TrackingResponse)
        self._repository: TrackingRepository = repository

    async def create_tracking(self, data: TrackingCreate) -> TrackingResponse:
        """
        Create a new tracking entry and save historical state.
        """
        logger.info("Creating tracking for cargo_id=%s", data.cargo_id)
        tracking = await self._repository.create_with_history(data.model_dump())
        logger.debug("Tracking created: %s", tracking)
        return TrackingResponse.model_validate(tracking)

    async def get_tracking(self, tracking_id: int) -> Optional[TrackingResponse]:
        """
        Retrieve tracking by its unique ID.
        """
        logger.info("Fetching tracking by ID: %s", tracking_id)
        tracking = await self._repository.get_by_id(tracking_id)
        if not tracking:
            logger.warning("Tracking not found: ID %s", tracking_id)
            return None
        logger.debug("Tracking found: %s", tracking)
        return TrackingResponse.model_validate(tracking)

    async def get_all_tracking(self) -> List[TrackingResponse]:
        """
        Retrieve all tracking records.
        """
        logger.info("Fetching all tracking records")
        tracking = await self._repository.get_all()
        logger.debug("Total tracking records found: %d", len(tracking))
        return [TrackingResponse.model_validate(t) for t in tracking]

    async def update_tracking(
        self, tracking_id: int, data: TrackingUpdate
    ) -> Optional[TrackingResponse]:
        """
        Update tracking and log changes to tracking history.
        """
        logger.info("Updating tracking ID: %s", tracking_id)
        tracking = await self._repository.update_with_history(
            tracking_id, data.model_dump(exclude_unset=True)
        )
        if not tracking:
            logger.warning("Tracking update failed: ID %s not found", tracking_id)
            return None
        logger.debug("Tracking updated: %s", tracking)
        return TrackingResponse.model_validate(tracking)

    async def delete_tracking(self, tracking_id: int) -> bool:
        """
        Delete a tracking entry by ID.
        """
        logger.info("Deleting tracking ID: %s", tracking_id)
        success = await self._repository.delete(tracking_id)
        if success:
            logger.debug("Tracking deleted: ID %s", tracking_id)
        else:
            logger.warning("Failed to delete tracking: ID %s", tracking_id)
        return success

    async def get_tracking_by_cargo(self, cargo_id: int) -> List[TrackingResponse]:
        """
        Get all tracking records for a specific cargo.
        """
        logger.info("Fetching tracking for cargo ID: %s", cargo_id)
        tracking = await self._repository.find_by_cargo_id(cargo_id)
        logger.debug("Tracking records found: %d", len(tracking))
        return [TrackingResponse.model_validate(t) for t in tracking]

    async def get_tracking_by_vessel(self, vessel_id: int) -> List[TrackingResponse]:
        """
        Get all tracking records for a specific vessel.
        """
        logger.info("Fetching tracking for vessel ID: %s", vessel_id)
        tracking = await self._repository.find_by_vessel_id(vessel_id)
        logger.debug("Tracking records found: %d", len(tracking))
        return [TrackingResponse.model_validate(t) for t in tracking]

    async def get_latest_tracking_by_cargo(
        self, cargo_id: int
    ) -> Optional[TrackingResponse]:
        """
        Retrieve the latest tracking record for a given cargo.
        """
        logger.info("Fetching latest tracking for cargo ID: %s", cargo_id)
        tracking = await self._repository.find_latest_by_cargo_id(cargo_id)
        if not tracking:
            logger.warning("No tracking record found for cargo ID: %s", cargo_id)
            return None
        logger.debug("Latest tracking record: %s", tracking)
        return TrackingResponse.model_validate(tracking)

    async def get_tracking_history(
        self, cargo_id: int
    ) -> List[TrackingHistoryResponse]:
        """
        Get full historical tracking records for a cargo.
        """
        logger.info("Fetching tracking history for cargo ID: %s", cargo_id)
        history = await self._repository.get_tracking_history(cargo_id)
        logger.debug("Tracking history records found: %d", len(history))
        return [TrackingHistoryResponse.model_validate(h) for h in history]

    async def get_cargoes_by_tracking_status(
        self, status: TrackingStatus
    ) -> List[TrackingResponse]:
        """
        Get all tracking records filtered by tracking status.
        """
        logger.info("Fetching cargoes by tracking status: %s", status.value)
        tracking = await self._repository.find_cargoes_by_status(status)
        logger.debug("Cargoes found with status '%s': %d", status.value, len(tracking))
        return [TrackingResponse.model_validate(t) for t in tracking]
