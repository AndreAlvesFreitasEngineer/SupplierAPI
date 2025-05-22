import logging
from typing import List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status

from app.domain.models.client import Client
from app.repositories.client_repository import ClientRepository
from app.api.schemas.client_schema import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientSummary,
)
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class ClientService(BaseService[ClientResponse]):
    def __init__(self, repository: ClientRepository):
        # Initialize the service with the given repository and response schema
        super().__init__(repository)
        self._repository: ClientRepository = repository

    async def create_client(self, client_data: ClientCreate) -> ClientResponse:
        """
        Create a new client after checking for duplicate email and tax ID.
        """
        logger.info("Creating client with email: %s", client_data.contact_email)

        if await self._repository.find_by_email(client_data.contact_email):
            logger.warning(
                "Client already exists with email: %s", client_data.contact_email
            )
            raise ValueError(
                f"Client with email '{client_data.contact_email}' already exists."
            )

        if client_data.tax_id and await self._repository.find_by_tax_id(
            client_data.tax_id
        ):
            logger.warning("Duplicate Tax ID: %s", client_data.tax_id)
            raise ValueError(f"Tax ID '{client_data.tax_id}' is already registered.")

        try:
            created = await self._repository.create(client_data.model_dump())
            logger.debug("Client created successfully: %s", created)
            return ClientResponse.model_validate(created)
        except IntegrityError as e:
            logger.exception("Integrity error while creating client")
            if "UNIQUE constraint failed: client.tax_id" in str(e):
                raise ValueError("Tax ID must be unique") from e
            raise

    async def update_client(
        self, client_id: int, client_data: ClientUpdate
    ) -> Optional[ClientResponse]:
        """
        Update a client's information if they exist.
        """
        logger.info("Updating client with ID: %s", client_id)

        existing_client = await self._repository.get_by_id(client_id)
        if not existing_client:
            logger.warning("Client not found for update: ID %s", client_id)
            return None

        # Check if email is being updated and ensure it's not already used
        if (
            client_data.contact_email
            and client_data.contact_email != existing_client.contact_email
        ):
            if await self._repository.find_by_email(client_data.contact_email):
                logger.warning("Email already in use: %s", client_data.contact_email)
                raise ValueError("Email already in use")

        updated_fields = client_data.model_dump(exclude_unset=True)
        updated = await self._repository.update(client_id, updated_fields)

        logger.debug("Client updated: %s", updated)
        return ClientResponse.model_validate(updated)

    async def delete_client(self, client_id: int) -> bool:
        """
        Delete a client by their ID.
        """
        logger.info("Deleting client with ID: %s", client_id)
        success = await self._repository.delete(client_id)
        if success:
            logger.debug("Client deleted: ID %s", client_id)
        else:
            logger.warning("Client not found or failed to delete: ID %s", client_id)
        return success

    async def search_clients_by_name(self, name: str) -> List[ClientSummary]:
        """
        Return a list of clients with matching or similar names.
        """
        logger.info("Searching clients by name: %s", name)
        clients = await self._repository.find_by_name(name)
        logger.debug("Clients found: %d", len(clients))
        return [ClientSummary.model_validate(c) for c in clients]

    async def get_client_by_email(self, email: str) -> Optional[ClientResponse]:
        """
        Look up a client by their email address.
        """
        logger.info("Getting client by email: %s", email)
        client = await self._repository.find_by_email(email)
        if client:
            logger.debug("Client found: %s", client)
            return ClientResponse.model_validate(client)
        logger.warning("Client not found with email: %s", email)
        return None

    async def get_client(self, client_id: int) -> ClientResponse:
        """
        Retrieve detailed client data by ID.
        """
        logger.info("Fetching client with ID: %s", client_id)
        client = await self._repository.get_by_id(client_id)
        if not client:
            logger.warning("Client not found: ID %s", client_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
            )
        logger.debug("Client retrieved: %s", client)
        return ClientResponse.model_validate(client)
