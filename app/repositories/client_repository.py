import logging
from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.client import Client
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ClientRepository(BaseRepository[Client]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Client)

    async def find_by_email(self, email: str) -> Optional[Client]:
        """
        Find a client by exact email (case-insensitive).
        """
        if not email:
            logger.warning("Attempted to search client with empty email")
            return None

        logger.info("Searching for client with email: %s", email)
        result = await self._session.execute(
            select(Client).where(Client.contact_email.ilike(email))
        )
        client = result.scalars().first()

        if client:
            logger.debug("Client found with email: %s", email)
        else:
            logger.warning("No client found with email: %s", email)

        return client

    async def find_by_name(self, name: str) -> Sequence[Client]:
        """
        Search clients by partial match on company name (case-insensitive).
        """
        logger.info("Searching for clients with name like: %s", name)
        result = await self._session.execute(
            select(Client).where(Client.company_name.ilike(f"%{name}%"))
        )
        clients = result.scalars().all()
        logger.debug("Clients found with name like '%s': %d", name, len(clients))
        return clients

    async def find_by_tax_id(self, tax_id: str) -> Optional[Client]:
        """
        Find a client by exact Tax ID (case-sensitive).
        """
        logger.info("Searching for client with tax ID: %s", tax_id)
        result = await self._session.execute(
            select(Client).where(Client.tax_id == tax_id)
        )
        client = result.scalars().first()

        if client:
            logger.debug("Client found with tax ID: %s", tax_id)
        else:
            logger.warning("No client found with tax ID: %s", tax_id)

        return client
