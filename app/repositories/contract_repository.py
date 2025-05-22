import logging
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums.status import ContractStatus
from app.domain.models.contract import Contract
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ContractRepository(BaseRepository[Contract]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Contract)

    async def find_by_client_id(self, client_id: int) -> Sequence[Contract]:
        """
        Retrieve all contracts associated with a specific client ID.
        """
        logger.info("Fetching contracts for client ID: %s", client_id)
        stmt = select(Contract).where(Contract.client_id == client_id)
        result = await self._session.execute(stmt)
        contracts = result.scalars().all()
        logger.debug("Contracts found for client ID %s: %d", client_id, len(contracts))
        return contracts

    async def find_by_contract_number(self, contract_number: str) -> Optional[Contract]:
        """
        Retrieve a contract by its unique contract number.
        """
        logger.info("Searching for contract with number: %s", contract_number)
        stmt = select(Contract).where(Contract.contract_number == contract_number)
        result = await self._session.execute(stmt)
        contract = result.scalar_one_or_none()
        if contract:
            logger.debug("Contract found with number: %s", contract_number)
        else:
            logger.warning("No contract found with number: %s", contract_number)
        return contract

    async def find_by_status(self, status: ContractStatus) -> Sequence[Contract]:
        """
        Retrieve all contracts with a given status (e.g., ACTIVE, EXPIRED).
        """
        logger.info("Fetching contracts with status: %s", status.value)
        stmt = select(Contract).where(Contract.status == status.value)
        result = await self._session.execute(stmt)
        contracts = result.scalars().all()
        logger.debug(
            "Contracts found with status '%s': %d", status.value, len(contracts)
        )
        return contracts

    async def find_active_in_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> Sequence[Contract]:
        """
        Retrieve all active contracts overlapping a given date range.
        """
        logger.info(
            "Fetching active contracts in date range: %s - %s", start_date, end_date
        )
        stmt = select(Contract).where(
            and_(
                Contract.status == ContractStatus.ACTIVE.value,
                Contract.start_date <= end_date,
                Contract.end_date >= start_date,
            )
        )
        result = await self._session.execute(stmt)
        contracts = result.scalars().all()
        logger.debug("Active contracts found in range: %d", len(contracts))
        return contracts

    async def find_active_contracts(self) -> Sequence[Contract]:
        """
        Retrieve all currently active contracts (i.e., today is between start and end dates).
        """
        now = datetime.now()
        logger.info("Fetching contracts active as of now: %s", now)
        stmt = select(Contract).where(
            and_(
                Contract.start_date <= now,
                Contract.end_date >= now,
            )
        )
        result = await self._session.execute(stmt)
        contracts = result.scalars().all()
        logger.debug("Currently active contracts found: %d", len(contracts))
        return contracts
