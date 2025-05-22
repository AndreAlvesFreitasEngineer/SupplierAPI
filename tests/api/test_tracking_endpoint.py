import pytest
from httpx import AsyncClient
from datetime import datetime
from unittest.mock import AsyncMock
from app.main import app
from app.api.schemas.tracking_schema import TrackingResponse, TrackingHistoryResponse
from app.domain.enums.status import TrackingStatus
from app.dependency import get_tracking_service


def tracking_response_mock(**overrides):
    base = dict(
        id=1,
        cargo_id=1,
        vessel_id=1,
        location="Port A",
        status=TrackingStatus.IN_TRANSIT.value,
        timestamp=datetime.utcnow(),
        notes="All good",
        temperature=18.0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    return TrackingResponse(**{**base, **overrides})


def tracking_history_mock():
    return [
        TrackingHistoryResponse(
            id=1,
            tracking_id=1,
            cargo_id=1,
            vessel_id=1,
            previous_status="loading",
            new_status="in_transit",
            previous_location="Port A",
            new_location="Port B",
            timestamp=datetime.utcnow(),
            notes="Moved",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    ]


@pytest.mark.asyncio
async def test_create_tracking(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.create_tracking.return_value = tracking_response_mock()
    app.dependency_overrides[get_tracking_service] = lambda: mock_service

    response = await client.post(
        "/api/v1/trackings/",
        json={
            "cargo_id": 1,
            "vessel_id": 1,
            "location": "Port A",
            "status": "in_transit",
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_add_tracking(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.create_tracking.return_value = tracking_response_mock()
    app.dependency_overrides[get_tracking_service] = lambda: mock_service

    response = await client.post(
        "/api/v1/trackings/",
        json={
            "cargo_id": 1,
            "vessel_id": 1,
            "location": "Port B",
            "status": "in_transit",
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_add_tracking_again(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.create_tracking.return_value = tracking_response_mock()
    app.dependency_overrides[get_tracking_service] = lambda: mock_service

    response = await client.post(
        "/api/v1/trackings/",
        json={
            "cargo_id": 1,
            "vessel_id": 1,
            "location": "Port C",
            "status": "unloading",
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_get_tracking(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_tracking.return_value = tracking_response_mock()
    app.dependency_overrides[get_tracking_service] = lambda: mock_service

    response = await client.get("/api/v1/trackings/1")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_delete_tracking(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.delete_tracking.return_value = True
    app.dependency_overrides[get_tracking_service] = lambda: mock_service

    response = await client.delete("/api/v1/trackings/1")
    app.dependency_overrides.clear()

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_by_cargo(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_tracking_by_cargo.return_value = [tracking_response_mock()]
    app.dependency_overrides[get_tracking_service] = lambda: mock_service

    response = await client.get("/api/v1/trackings/by-cargo/1")
    app.dependency_overrides.clear()

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_latest_tracking(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_latest_tracking_by_cargo.return_value = tracking_response_mock()
    app.dependency_overrides[get_tracking_service] = lambda: mock_service

    response = await client.get("/api/v1/trackings/latest/1")
    app.dependency_overrides.clear()

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_tracking_history(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_tracking_history.return_value = tracking_history_mock()
    app.dependency_overrides[get_tracking_service] = lambda: mock_service

    response = await client.get("/api/v1/trackings/history/1")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_by_status(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_cargoes_by_tracking_status.return_value = [
        tracking_response_mock(status="delivered")
    ]
    app.dependency_overrides[get_tracking_service] = lambda: mock_service

    response = await client.get("/api/v1/trackings/status/delivered")
    app.dependency_overrides.clear()

    assert response.status_code == 200
