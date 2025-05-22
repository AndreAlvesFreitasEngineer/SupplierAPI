from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from starlette import status

from app.api.schemas.tracking_schema import (
    TrackingCreate,
    TrackingUpdate,
    TrackingResponse,
    TrackingHistoryResponse,
)
from app.api.schemas.base_schema import PaginatedResponse
from app.domain.enums.status import TrackingStatus
from app.services.tracking_service import TrackingService
from app.dependency import get_tracking_service

router = APIRouter(prefix="/trackings", tags=["Tracking"])


@router.post(
    "/",
    response_model=TrackingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new tracking record",
    responses={
        201: {"model": TrackingResponse},
        400: {"description": "Invalid input"},
        422: {"description": "Validation error"},
    },
)
async def add_tracking(
    data: TrackingCreate,
    service: TrackingService = Depends(get_tracking_service),
) -> TrackingResponse:
    """
    Create a new tracking record for a cargo.

    - **data**: Required details such as cargo ID, vessel ID, location, status
    """
    return await service.create_tracking(data)


@router.get(
    "/{tracking_id}",
    response_model=TrackingResponse,
    summary="Get tracking record by ID",
    responses={
        200: {"model": TrackingResponse},
        404: {"description": "Tracking not found"},
    },
)
async def get_tracking(
    tracking_id: int,
    service: TrackingService = Depends(get_tracking_service),
) -> TrackingResponse:
    """
    Fetch a single tracking record by its unique ID.

    - **tracking_id**: ID of the tracking record
    """
    tracking = await service.get_tracking(tracking_id)
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking not found")
    return tracking


@router.get(
    "/",
    response_model=PaginatedResponse[TrackingResponse],
    summary="List tracking records (paginated)",
    responses={
        200: {"model": PaginatedResponse[TrackingResponse]},
        400: {"description": "Invalid query parameters"},
    },
)
async def list_trackings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Records per page"),
    service: TrackingService = Depends(get_tracking_service),
) -> PaginatedResponse[TrackingResponse]:
    """
    Get a paginated list of tracking records.
    """
    items, total = await service.get_paginated(page=page, page_size=page_size)
    return PaginatedResponse[TrackingResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.put(
    "/{tracking_id}",
    response_model=TrackingResponse,
    summary="Update tracking record",
    responses={
        200: {"model": TrackingResponse},
        404: {"description": "Tracking not found"},
        422: {"description": "Validation error"},
    },
)
async def update_tracking(
    tracking_id: int,
    data: TrackingUpdate,
    service: TrackingService = Depends(get_tracking_service),
) -> TrackingResponse:
    """
    Update details of an existing tracking record.

    - **tracking_id**: ID of the record to update
    - **data**: Fields to update
    """
    updated = await service.update_tracking(tracking_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Tracking not found or unchanged")
    return updated


@router.delete(
    "/{tracking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete tracking record",
    responses={
        204: {"description": "Deleted successfully"},
        404: {"description": "Tracking not found"},
    },
)
async def delete_tracking(
    tracking_id: int,
    service: TrackingService = Depends(get_tracking_service),
) -> None:
    """
    Delete a tracking record by ID.

    - **tracking_id**: ID to delete
    """
    if not await service.delete_tracking(tracking_id):
        raise HTTPException(status_code=404, detail="Tracking not found")


@router.get(
    "/by-cargo/{cargo_id}",
    response_model=List[TrackingResponse],
    summary="Get tracking by cargo ID",
    responses={
        200: {"model": List[TrackingResponse]},
        404: {"description": "No records found"},
    },
)
async def get_tracking_by_cargo(
    cargo_id: int,
    service: TrackingService = Depends(get_tracking_service),
) -> List[TrackingResponse]:
    """
    Retrieve all tracking records linked to a cargo.

    - **cargo_id**: Cargo ID to filter by
    """
    return await service.get_tracking_by_cargo(cargo_id)


@router.get(
    "/by-vessel/{vessel_id}",
    response_model=List[TrackingResponse],
    summary="Get tracking by vessel ID",
    responses={
        200: {"model": List[TrackingResponse]},
        404: {"description": "No records found"},
    },
)
async def get_tracking_by_vessel(
    vessel_id: int,
    service: TrackingService = Depends(get_tracking_service),
) -> List[TrackingResponse]:
    """
    Retrieve all tracking records for a vessel.

    - **vessel_id**: Vessel ID to filter by
    """
    return await service.get_tracking_by_vessel(vessel_id)


@router.get(
    "/latest/{cargo_id}",
    response_model=TrackingResponse,
    summary="Get latest tracking for cargo",
    responses={
        200: {"model": TrackingResponse},
        404: {"description": "No tracking found"},
    },
)
async def get_latest_tracking(
    cargo_id: int,
    service: TrackingService = Depends(get_tracking_service),
) -> TrackingResponse:
    """
    Fetch the most recent tracking entry for a given cargo.

    - **cargo_id**: Cargo ID to filter by
    """
    tracking = await service.get_latest_tracking_by_cargo(cargo_id)
    if not tracking:
        raise HTTPException(status_code=404, detail="No tracking found")
    return tracking


@router.get(
    "/history/{cargo_id}",
    response_model=List[TrackingHistoryResponse],
    summary="Get tracking history for cargo",
    responses={
        200: {"model": List[TrackingHistoryResponse]},
        404: {"description": "No history found"},
    },
)
async def get_tracking_history(
    cargo_id: int,
    service: TrackingService = Depends(get_tracking_service),
) -> List[TrackingHistoryResponse]:
    """
    Retrieve the full history of tracking events for a cargo.

    - **cargo_id**: Cargo ID to view history for
    """
    return await service.get_tracking_history(cargo_id)


@router.get(
    "/status/{status}",
    response_model=List[TrackingResponse],
    summary="Get tracking by status",
    responses={
        200: {"model": List[TrackingResponse]},
        404: {"description": "No tracking found"},
    },
)
async def get_cargoes_by_status(
    status: TrackingStatus,
    service: TrackingService = Depends(get_tracking_service),
) -> List[TrackingResponse]:
    """
    Retrieve all cargoes filtered by a tracking status.

    - **status**: Status value (e.g. IN_TRANSIT, DELIVERED)
    """
    return await service.get_cargoes_by_tracking_status(status)
