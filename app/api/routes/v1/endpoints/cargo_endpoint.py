import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List

from starlette import status

from app.api.schemas.cargo_schema import (
    CargoCreate,
    CargoUpdate,
    CargoResponse,
    CargoStatus,
)
from app.api.schemas.base_schema import PaginatedResponse
from app.services.cargo_service import CargoService
from app.dependency import get_cargo_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cargo", tags=["Cargo"])


@router.post(
    "/",
    response_model=CargoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cargo",
    responses={
        201: {"model": CargoResponse},
        400: {"description": "Invalid input data"},
        422: {"description": "Validation error"},
    },
)
async def create_cargo(
    data: CargoCreate, service: CargoService = Depends(get_cargo_service)
) -> CargoResponse:
    """
    Create a new cargo entry.

    - **data**: The details for the cargo, including contract, destination, weight, etc.
    """
    return await service.create_cargo(data)


@router.get(
    "/{cargo_id}",
    response_model=CargoResponse,
    summary="Get cargo by ID",
    responses={
        200: {"model": CargoResponse},
        404: {"description": "Cargo not found"},
    },
)
async def get_cargo(
    cargo_id: int, service: CargoService = Depends(get_cargo_service)
) -> CargoResponse:
    """
    Retrieve a cargo entry by its ID.
    """
    cargo = await service.get_cargo(cargo_id)
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo not found")
    return cargo


@router.get(
    "/{cargo_id}/with-tracking",
    response_model=CargoResponse,
    summary="Get cargo with tracking info",
    responses={
        200: {"model": CargoResponse},
        404: {"description": "Cargo not found"},
    },
)
async def get_cargo_with_tracking(
    cargo_id: int, service: CargoService = Depends(get_cargo_service)
) -> CargoResponse:
    """
    Retrieve cargo details along with its full tracking history.
    """
    cargo = await service.get_cargo_with_tracking(cargo_id)
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo not found")
    return cargo


@router.get(
    "/",
    response_model=PaginatedResponse[CargoResponse],
    summary="Get paginated list of all cargoes",
    responses={
        200: {"model": PaginatedResponse[CargoResponse]},
        400: {"description": "Invalid pagination parameters"},
    },
)
async def list_cargoes(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    service: CargoService = Depends(get_cargo_service),
) -> PaginatedResponse[CargoResponse]:
    """
    Return paginated list of all cargo entries.
    """
    skip = (page - 1) * page_size
    items, total = await service.get_cargoes_paginated(skip=skip, limit=page_size)
    return PaginatedResponse[CargoResponse](
        items=items, total=total, page=page, page_size=page_size
    )


@router.put(
    "/{cargo_id}",
    response_model=CargoResponse,
    summary="Update an existing cargo",
    responses={
        200: {"model": CargoResponse},
        400: {"description": "Invalid input data"},
        404: {"description": "Cargo not found"},
        422: {"description": "Validation error"},
    },
)
async def update_cargo(
    cargo_id: int, data: CargoUpdate, service: CargoService = Depends(get_cargo_service)
) -> CargoResponse:
    """
    Update an existing cargo by ID.

    - **cargo_id**: The ID of the cargo to update
    - **data**: Fields to update
    """
    updated = await service.update_cargo(cargo_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Cargo not found")
    return updated


@router.delete(
    "/{cargo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a cargo",
    responses={
        204: {"description": "Cargo deleted successfully"},
        404: {"description": "Cargo not found"},
    },
)
async def delete_cargo(
    cargo_id: int, service: CargoService = Depends(get_cargo_service)
) -> None:
    """
    Delete a cargo entry by its ID.
    """
    if not await service.delete_cargo(cargo_id):
        raise HTTPException(status_code=404, detail="Cargo not found")


@router.get(
    "/search/by-contract/{contract_id}",
    response_model=List[CargoResponse],
    summary="Get cargoes by contract ID",
    responses={
        200: {"model": List[CargoResponse]},
        404: {"description": "No cargoes found for this contract"},
    },
)
async def get_cargoes_by_contract(
    contract_id: int, service: CargoService = Depends(get_cargo_service)
) -> List[CargoResponse]:
    """
    Get all cargoes linked to a specific contract ID.
    """
    return await service.get_cargoes_by_contract(contract_id)


@router.get(
    "/search/by-status",
    response_model=List[CargoResponse],
    summary="Get cargoes by status",
    responses={
        200: {"model": List[CargoResponse]},
        404: {"description": "No cargoes found for this status"},
    },
)
async def get_cargoes_by_status(
    status: CargoStatus = Query(..., description="Cargo status to filter by"),
    service: CargoService = Depends(get_cargo_service),
) -> List[CargoResponse]:
    """
    Get cargoes that have a specific status (e.g., PENDING, DELIVERED).
    """
    return await service.get_cargoes_by_status(status)


@router.get(
    "/search/by-destination",
    response_model=List[CargoResponse],
    summary="Get cargoes by destination",
    responses={
        200: {"model": List[CargoResponse]},
        404: {"description": "No cargoes found for this destination"},
    },
)
async def get_cargoes_by_destination(
    destination: str = Query(
        ..., min_length=2, description="Destination to search for"
    ),
    service: CargoService = Depends(get_cargo_service),
) -> List[CargoResponse]:
    """
    Get cargoes that are being delivered to a specified destination (supports partial match).
    """
    return await service.get_cargoes_by_destination(destination)
