from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from starlette import status

from app.api.schemas.vessel_schema import (
    VesselCreate,
    VesselUpdate,
    VesselResponse,
    VesselStatus,
)
from app.api.schemas.base_schema import PaginatedResponse
from app.services.vessel_service import VesselService
from app.dependency import get_vessel_service

router = APIRouter(prefix="/vessels", tags=["Vessels"])


@router.post(
    "/",
    response_model=VesselResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new vessel",
    responses={
        201: {"model": VesselResponse},
        400: {"description": "Invalid input"},
        422: {"description": "Validation error"},
    },
)
async def create_vessel(
    data: VesselCreate,
    service: VesselService = Depends(get_vessel_service),
) -> VesselResponse:
    """
    Register a new vessel in the system.

    - **data**: Required details including name, capacity, status, etc.
    """
    return await service.create_vessel(data)


@router.get(
    "/{vessel_id}",
    response_model=VesselResponse,
    summary="Get vessel by ID",
    responses={
        200: {"model": VesselResponse},
        404: {"description": "Vessel not found"},
    },
)
async def get_vessel(
    vessel_id: int,
    service: VesselService = Depends(get_vessel_service),
) -> VesselResponse:
    """
    Retrieve a vessel's detailed information using its ID.

    - **vessel_id**: ID of the vessel
    """
    vessel = await service.get_vessel(vessel_id)
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")
    return vessel


@router.get(
    "/",
    response_model=PaginatedResponse[VesselResponse],
    summary="List vessels (paginated)",
    responses={
        200: {"model": PaginatedResponse[VesselResponse]},
        400: {"description": "Invalid pagination parameters"},
    },
)
async def list_vessels(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    service: VesselService = Depends(get_vessel_service),
) -> PaginatedResponse[VesselResponse]:
    """
    Get a paginated list of all registered vessels.

    - **page**: Current page number
    - **page_size**: Number of vessels per page
    """
    items, total = await service.get_paginated(page=page, page_size=page_size)
    return PaginatedResponse[VesselResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.put(
    "/{vessel_id}",
    response_model=VesselResponse,
    summary="Update vessel",
    responses={
        200: {"model": VesselResponse},
        400: {"description": "Invalid input"},
        404: {"description": "Vessel not found"},
        422: {"description": "Validation error"},
    },
)
async def update_vessel(
    vessel_id: int,
    data: VesselUpdate,
    service: VesselService = Depends(get_vessel_service),
) -> VesselResponse:
    """
    Update an existing vessel.

    - **vessel_id**: ID of the vessel to update
    - **data**: Fields to update
    """
    updated = await service.update_vessel(vessel_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Vessel not found")
    return updated


@router.delete(
    "/{vessel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete vessel",
    responses={
        204: {"description": "Vessel deleted successfully"},
        404: {"description": "Vessel not found"},
    },
)
async def delete_vessel(
    vessel_id: int,
    service: VesselService = Depends(get_vessel_service),
) -> None:
    """
    Remove a vessel from the system.

    - **vessel_id**: The vessel's ID
    """
    if not await service.delete_vessel(vessel_id):
        raise HTTPException(status_code=404, detail="Vessel not found")


@router.get(
    "/search/by-name",
    response_model=VesselResponse,
    summary="Search vessel by name",
    responses={
        200: {"model": VesselResponse},
        404: {"description": "Vessel not found"},
    },
)
async def search_vessel_by_name(
    name: str = Query(..., min_length=2, description="Exact name of the vessel"),
    service: VesselService = Depends(get_vessel_service),
) -> VesselResponse:
    """
    Retrieve a vessel by its exact name.

    - **name**: Full vessel name
    """
    vessel = await service.get_vessel_by_name(name)
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")
    return vessel


@router.get(
    "/search/by-status",
    response_model=List[VesselResponse],
    summary="Get vessels by status",
    responses={
        200: {"model": List[VesselResponse]},
        404: {"description": "No vessels found"},
    },
)
async def vessels_by_status(
    status: VesselStatus = Query(
        ..., description="Vessel status (ACTIVE, MAINTENANCE...)"
    ),
    service: VesselService = Depends(get_vessel_service),
) -> List[VesselResponse]:
    """
    Retrieve all vessels filtered by status.

    - **status**: Operational status (ACTIVE, MAINTENANCE, etc.)
    """
    return await service.get_vessels_by_status(status)


@router.get(
    "/search/by-location",
    response_model=List[VesselResponse],
    summary="Get vessels by location",
    responses={
        200: {"model": List[VesselResponse]},
        404: {"description": "No vessels found"},
    },
)
async def vessels_by_location(
    location: str = Query(..., min_length=2, description="Current vessel location"),
    service: VesselService = Depends(get_vessel_service),
) -> List[VesselResponse]:
    """
    Find all vessels currently at a specific location.

    - **location**: Port or location string (partial match supported)
    """
    return await service.get_vessels_by_location(location)


@router.get(
    "/search/available",
    response_model=List[VesselResponse],
    summary="Get available vessels by minimum capacity",
    responses={
        200: {"model": List[VesselResponse]},
        404: {"description": "No vessels available"},
    },
)
async def available_vessels(
    min_capacity: float = Query(
        0, ge=0, description="Minimum required capacity in tons"
    ),
    service: VesselService = Depends(get_vessel_service),
) -> List[VesselResponse]:
    """
    Retrieve vessels marked as available and meeting the minimum capacity.

    - **min_capacity**: Minimum cargo capacity in tons (optional)
    """
    return await service.get_available_vessels(min_capacity)
