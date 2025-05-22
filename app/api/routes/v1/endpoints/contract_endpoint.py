from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from datetime import datetime
from starlette import status

from app.api.schemas.contract_schema import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractStatus,
)
from app.api.schemas.base_schema import PaginatedResponse
from app.services.contract_service import ContractService
from app.dependency import get_contract_service

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.post(
    "/",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new contract",
    responses={
        201: {"model": ContractResponse},
        400: {"description": "Invalid input data"},
        422: {"description": "Validation error"},
    },
)
async def create_contract(
    data: ContractCreate,
    service: ContractService = Depends(get_contract_service),
) -> ContractResponse:
    """
    Create a new contract record.

    - **data**: Includes client reference, terms, pricing, and status
    """
    return await service.create_contract(data)


@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    summary="Get contract by ID",
    responses={
        200: {"model": ContractResponse},
        404: {"description": "Contract not found"},
    },
)
async def get_contract(
    contract_id: int,
    service: ContractService = Depends(get_contract_service),
) -> ContractResponse:
    """
    Retrieve a contract by its ID.

    - **contract_id**: Unique identifier of the contract
    """
    contract = await service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.get(
    "/",
    response_model=PaginatedResponse[ContractResponse],
    summary="List contracts (paginated)",
    responses={
        200: {"model": PaginatedResponse[ContractResponse]},
        400: {"description": "Invalid pagination parameters"},
    },
)
async def list_contracts(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    service: ContractService = Depends(get_contract_service),
) -> PaginatedResponse[ContractResponse]:
    """
    Get a paginated list of contracts.

    - **page**: Page number
    - **page_size**: Number of contracts per page
    """
    items, total = await service.get_paginated(page=page, page_size=page_size)
    return PaginatedResponse[ContractResponse](
        items=items, total=total, page=page, page_size=page_size
    )


@router.put(
    "/{contract_id}",
    response_model=ContractResponse,
    summary="Update contract details",
    responses={
        200: {"model": ContractResponse},
        400: {"description": "Invalid data"},
        404: {"description": "Contract not found"},
        422: {"description": "Validation error"},
    },
)
async def update_contract(
    contract_id: int,
    data: ContractUpdate,
    service: ContractService = Depends(get_contract_service),
) -> ContractResponse:
    """
    Update an existing contract.

    - **contract_id**: Contract to update
    - **data**: Fields to be updated
    """
    updated = await service.update_contract(contract_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Contract not found")
    return updated


@router.delete(
    "/{contract_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete contract",
    responses={
        204: {"description": "Successfully deleted"},
        404: {"description": "Contract not found"},
    },
)
async def delete_contract(
    contract_id: int,
    service: ContractService = Depends(get_contract_service),
) -> None:
    """
    Delete a contract by its ID.

    - **contract_id**: Contract to delete
    """
    if not await service.delete_contract(contract_id):
        raise HTTPException(status_code=404, detail="Contract not found")


@router.get(
    "/search/by-client/{client_id}",
    response_model=List[ContractResponse],
    summary="Get contracts by client ID",
    responses={
        200: {"model": List[ContractResponse]},
        404: {"description": "No contracts found"},
    },
)
async def get_contracts_by_client(
    client_id: int,
    service: ContractService = Depends(get_contract_service),
) -> List[ContractResponse]:
    """
    List all contracts for a specific client.

    - **client_id**: Client’s unique ID
    """
    return await service.get_contracts_by_client(client_id)


@router.get(
    "/search/by-status",
    response_model=List[ContractResponse],
    summary="Get contracts by status",
    responses={
        200: {"model": List[ContractResponse]},
        404: {"description": "No contracts found"},
    },
)
async def get_contracts_by_status(
    status: ContractStatus = Query(..., description="Filter contracts by status"),
    service: ContractService = Depends(get_contract_service),
) -> List[ContractResponse]:
    """
    Retrieve all contracts with a given status.

    - **status**: One of `DRAFT`, `ACTIVE`, `EXPIRED`, etc.
    """
    return await service.get_contracts_by_status(status)


@router.get(
    "/search/active",
    response_model=List[ContractResponse],
    summary="Get active contracts in date range",
    responses={
        200: {"model": List[ContractResponse]},
        400: {"description": "Invalid date range"},
        404: {"description": "No active contracts found"},
    },
)
async def get_active_contracts_in_range(
    start_date: datetime = Query(..., description="Start of date range (ISO format)"),
    end_date: datetime = Query(..., description="End of date range (ISO format)"),
    service: ContractService = Depends(get_contract_service),
) -> List[ContractResponse]:
    """
    Retrieve contracts active between two dates.

    - **start_date**: Beginning of the time range
    - **end_date**: End of the time range
    """
    return await service.get_active_contracts_in_date_range(start_date, end_date)
