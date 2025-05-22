import logging
from typing import Optional

from sqlalchemy.exc import IntegrityError
from app.repositories.vessel_repository import VesselRepository
from app.api.schemas.vessel_schema import VesselCreate, VesselUpdate, VesselResponse
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class VesselService(BaseService[VesselResponse]):
    def __init__(self, repository: VesselRepository):
        super().__init__(repository)
        self._repository = repository

    async def create_vessel(self, vessel_data: VesselCreate) -> VesselResponse:
        """
        Create a new vessel, ensuring the name is unique.
        """
        logger.info("Attempting to create vessel: %s", vessel_data.name)
        existing = await self._repository.find_by_name(vessel_data.name)
        if existing:
            logger.warning("Vessel name already exists: %s", vessel_data.name)
            raise ValueError(f"Vessel with name '{vessel_data.name}' already exists")

        try:
            vessel = await self._repository.create(vessel_data.model_dump())
            logger.debug("Vessel created: %s", vessel)
        except IntegrityError as e:
            logger.exception("Database integrity error on vessel creation")
            raise ValueError("Database integrity error when creating vessel") from e

        return VesselResponse.model_validate(vessel)

    async def get_vessel(self, vessel_id: int) -> Optional[VesselResponse]:
        """
        Retrieve vessel by its unique ID.
        """
        logger.info("Fetching vessel with ID: %s", vessel_id)
        vessel = await self._repository.get_by_id(vessel_id)
        if vessel is None:
            logger.warning("Vessel not found: ID %s", vessel_id)
            return None
        logger.debug("Vessel retrieved: %s", vessel)
        return VesselResponse.model_validate(vessel)

    async def get_all_vessels(self) -> list[VesselResponse]:
        """
        Retrieve all vessels in the system.
        """
        logger.info("Fetching all vessels")
        vessels = await self._repository.get_all()
        logger.debug("Vessels retrieved: %d", len(vessels))
        return [VesselResponse.model_validate(v) for v in vessels]

    async def update_vessel(
        self, vessel_id: int, vessel_data: VesselUpdate
    ) -> Optional[VesselResponse]:
        """
        Update an existing vessel's data, ensuring name uniqueness.
        """
        logger.info("Updating vessel ID: %s", vessel_id)
        existing = await self._repository.get_by_id(vessel_id)
        if not existing:
            logger.warning("Vessel not found for update: ID %s", vessel_id)
            return None

        if vessel_data.name:
            duplicate = await self._repository.find_by_name(vessel_data.name)
            if duplicate and duplicate.id != vessel_id:
                logger.warning(
                    "Duplicate vessel name during update: %s", vessel_data.name
                )
                raise ValueError(
                    f"Vessel with name '{vessel_data.name}' already exists"
                )

        try:
            updated = await self._repository.update(
                vessel_id, vessel_data.model_dump(exclude_unset=True)
            )
            logger.debug("Vessel updated: %s", updated)
        except IntegrityError as e:
            logger.exception("Database integrity error on vessel update")
            raise ValueError("Database integrity error when updating vessel") from e

        return VesselResponse.model_validate(updated)

    async def delete_vessel(self, vessel_id: int) -> bool:
        """
        Delete a vessel by its ID.
        """
        logger.info("Deleting vessel with ID: %s", vessel_id)
        success = await self._repository.delete(vessel_id)
        if success:
            logger.debug("Vessel deleted: ID %s", vessel_id)
        else:
            logger.warning("Vessel deletion failed or not found: ID %s", vessel_id)
        return success

    async def get_vessel_by_name(self, name: str) -> Optional[VesselResponse]:
        """
        Find a vessel by its exact name.
        """
        logger.info("Searching vessel by name: %s", name)
        vessel = await self._repository.find_by_name(name)
        if vessel:
            logger.debug("Vessel found: %s", vessel)
            return VesselResponse.model_validate(vessel)
        logger.warning("Vessel not found with name: %s", name)
        return None

    async def get_vessels_by_status(self, status: str) -> list[VesselResponse]:
        """
        Get all vessels with a specific status.
        """
        logger.info("Fetching vessels with status: %s", status)
        vessels = await self._repository.find_by_status(status)
        logger.debug("Vessels found with status '%s': %d", status, len(vessels))
        return [VesselResponse.model_validate(v) for v in vessels]

    async def get_available_vessels(
        self, min_capacity: float = 0.0
    ) -> list[VesselResponse]:
        """
        Get all available vessels with at least the specified capacity.
        """
        logger.info("Fetching available vessels with min capacity: %.2f", min_capacity)
        vessels = await self._repository.find_available_vessels(min_capacity)
        logger.debug("Available vessels found: %d", len(vessels))
        return [VesselResponse.model_validate(v) for v in vessels]

    async def get_vessels_by_location(self, location: str) -> list[VesselResponse]:
        """
        Get vessels currently located at the specified location.
        """
        logger.info("Fetching vessels by location: %s", location)
        vessels = await self._repository.find_by_location(location)
        logger.debug("Vessels found at location '%s': %d", location, len(vessels))
        return [VesselResponse.model_validate(v) for v in vessels]
