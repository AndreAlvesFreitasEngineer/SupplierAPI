import logging
from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status

from app.api.schemas.base_schema import ErrorResponse, PaginatedResponse
from app.api.schemas.client_schema import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientSummary,
    PaginatedClientSummaryResponse,
)
from app.services.client_service import ClientService
from app.dependency import get_client_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post(
    "/",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new client",
    responses={
        201: {"model": ClientResponse},
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
async def create_client(
    client_data: ClientCreate,
    service: ClientService = Depends(get_client_service),
) -> ClientResponse:
    """
    Register a new client in the system.

    - **client_data**: All necessary client fields (name, email, tax ID, etc.)
    """
    return await service.create_client(client_data)


@router.get(
    "/",
    response_model=PaginatedClientSummaryResponse,
    summary="List clients (paginated)",
    responses={
        200: {"model": PaginatedClientSummaryResponse},
        400: {"model": ErrorResponse},
    },
)
async def get_all_clients(
    page: int = Query(1, gt=0, description="Page number (1-indexed)"),
    page_size: int = Query(10, gt=0, le=100, description="Number of clients per page"),
    service: ClientService = Depends(get_client_service),
) -> PaginatedClientSummaryResponse:
    """
    Retrieve a paginated list of all clients.

    - **page**: The current page number
    - **page_size**: Number of items per page (max 100)
    """
    clients, total = await service.get_paginated(page, page_size)
    return PaginatedClientSummaryResponse(
        items=clients,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Get client by ID",
    responses={
        200: {"model": ClientResponse},
        404: {"model": ErrorResponse},
    },
)
async def get_client(
    client_id: int, service: ClientService = Depends(get_client_service)
) -> ClientResponse:
    """
    Retrieve full client details by ID.

    - **client_id**: Unique identifier of the client
    """
    client = await service.get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    return client


@router.put(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Update client details",
    responses={
        200: {"model": ClientResponse},
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    service: ClientService = Depends(get_client_service),
) -> ClientResponse:
    """
    Update existing client information.

    - **client_id**: The client's ID
    - **client_data**: Fields to update (only the ones provided will be updated)
    """
    updated_client = await service.update_client(client_id, client_data)
    if not updated_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    return updated_client


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a client",
    responses={
        204: {"description": "Client successfully deleted"},
        404: {"model": ErrorResponse},
    },
)
async def delete_client(
    client_id: int, service: ClientService = Depends(get_client_service)
) -> None:
    """
    Delete a client by ID.

    - **client_id**: The client's ID
    """
    if not await service.delete_client(client_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )


@router.get(
    "/search/",
    response_model=List[ClientSummary],
    summary="Search clients by name",
    responses={
        200: {"model": List[ClientSummary]},
        400: {"model": ErrorResponse},
    },
)
async def search_clients(
    name: str = Query(
        ..., min_length=2, description="Name or partial name to search for"
    ),
    service: ClientService = Depends(get_client_service),
) -> List[ClientSummary]:
    """
    Search for clients using full or partial name.

    - **name**: Partial or full company name (min 2 characters)
    """
    return await service.search_clients_by_name(name)
