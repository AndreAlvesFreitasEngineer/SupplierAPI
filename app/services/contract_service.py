import logging
from typing import Optional, List
from sqlalchemy.exc import IntegrityError

from app.repositories.contract_repository import ContractRepository
from app.api.schemas.contract_schema import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
)
from app.domain.enums.status import ContractStatus
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class ContractService(BaseService[ContractResponse]):
    def __init__(self, repository: ContractRepository):
        super().__init__(repository)
        self._repository = repository

    async def create_contract(self, contract_data: ContractCreate) -> ContractResponse:
        """
        Create a new contract after validating uniqueness and dates.
        """
        logger.info("Creating contract with number: %s", contract_data.contract_number)

        if await self._repository.find_by_contract_number(
            contract_data.contract_number
        ):
            logger.warning(
                "Contract number already exists: %s", contract_data.contract_number
            )
            raise ValueError("Contract number already exists")

        if contract_data.start_date > contract_data.end_date:
            logger.warning("Invalid contract date range: start_date > end_date")
            raise ValueError("Start date cannot be after end date")

        try:
            contract = await self._repository.create(contract_data.model_dump())
            logger.debug("Contract created: %s", contract)
            return ContractResponse.model_validate(contract)
        except IntegrityError as e:
            logger.exception("Integrity error while creating contract")
            raise ValueError("Contract data integrity error") from e

    async def get_contract(self, contract_id: int) -> Optional[ContractResponse]:
        """
        Retrieve a single contract by its ID.
        """
        logger.info("Fetching contract with ID: %s", contract_id)
        contract = await self._repository.get_by_id(contract_id)
        if contract:
            logger.debug("Contract found: %s", contract)
            return ContractResponse.model_validate(contract)
        logger.warning("Contract not found: ID %s", contract_id)
        return None

    async def update_contract(
        self, contract_id: int, contract_data: ContractUpdate
    ) -> Optional[ContractResponse]:
        """
        Update an existing contract by ID, checking for duplicate numbers.
        """
        logger.info("Updating contract with ID: %s", contract_id)
        existing_contract = await self._repository.get_by_id(contract_id)
        if not existing_contract:
            logger.warning("Contract not found for update: ID %s", contract_id)
            return None

        if (
            contract_data.contract_number
            and contract_data.contract_number != existing_contract.contract_number
        ):
            if await self._repository.find_by_contract_number(
                contract_data.contract_number
            ):
                logger.warning(
                    "Duplicate contract number during update: %s",
                    contract_data.contract_number,
                )
                raise ValueError("Contract number already exists")

        updated_fields = contract_data.model_dump(exclude_unset=True)
        updated = await self._repository.update(contract_id, updated_fields)

        logger.debug("Contract updated: %s", updated)
        return ContractResponse.model_validate(updated)

    async def delete_contract(self, contract_id: int) -> bool:
        """
        Delete a contract by its ID.
        """
        logger.info("Deleting contract with ID: %s", contract_id)
        success = await self._repository.delete(contract_id)
        if success:
            logger.debug("Contract deleted: ID %s", contract_id)
        else:
            logger.warning("Contract not found or failed to delete: ID %s", contract_id)
        return success

    async def get_contracts_by_client(self, client_id: int) -> List[ContractResponse]:
        """
        Retrieve all contracts linked to a specific client.
        """
        logger.info("Fetching contracts by client ID: %s", client_id)
        contracts = await self._repository.find_by_client_id(client_id)
        logger.debug("Contracts found: %d", len(contracts))
        return [ContractResponse.model_validate(contract) for contract in contracts]

    async def get_contracts_by_status(
        self, status: ContractStatus
    ) -> List[ContractResponse]:
        """
        Filter contracts based on their status (e.g. ACTIVE, EXPIRED).
        """
        status_value = status.value if isinstance(status, ContractStatus) else status
        logger.info("Fetching contracts by status: %s", status_value)
        contracts = await self._repository.find_by_status(status_value)
        logger.debug("Contracts found: %d", len(contracts))
        return [ContractResponse.model_validate(contract) for contract in contracts]

    async def get_active_contracts_in_date_range(
        self, start_date, end_date
    ) -> List[ContractResponse]:
        """
        Retrieve all active contracts within a specified date range.
        """
        logger.info("Fetching active contracts from %s to %s", start_date, end_date)
        contracts = await self._repository.find_active_in_date_range(
            start_date, end_date
        )
        logger.debug("Active contracts found: %d", len(contracts))
        return [ContractResponse.model_validate(contract) for contract in contracts]
