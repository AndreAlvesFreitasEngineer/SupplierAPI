import pytest
from httpx import AsyncClient
from datetime import datetime
from unittest.mock import AsyncMock
from app.main import app
from app.dependency import get_vessel_service
from app.api.schemas.vessel_schema import VesselResponse, VesselStatus


def vessel_response_mock(**overrides):
    base = dict(
        id=1,
        name="Titan",
        capacity_weight=50000.0,
        year_built=2010,
        status=VesselStatus.ACTIVE.value,
        max_speed=24.0,
        current_location="Port A",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    return VesselResponse(**{**base, **overrides})


@pytest.mark.asyncio
async def test_create_vessel_success(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.create_vessel.return_value = vessel_response_mock()
    app.dependency_overrides[get_vessel_service] = lambda: mock_service

    response = await client.post(
        "/api/v1/vessels/",
        json={
            "name": "Titan",
            "capacity_weight": 50000.0,
            "year_built": 2010,
            "status": "active",
            "max_speed": 24.0,
            "current_location": "Port A",
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    assert response.json()["name"] == "Titan"


@pytest.mark.asyncio
async def test_get_vessel_found(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_vessel.return_value = vessel_response_mock()
    app.dependency_overrides[get_vessel_service] = lambda: mock_service

    response = await client.get("/api/v1/vessels/1")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_get_vessel_not_found(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_vessel.return_value = None
    app.dependency_overrides[get_vessel_service] = lambda: mock_service

    response = await client.get("/api/v1/vessels/999")
    app.dependency_overrides.clear()
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_vessels_success(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_paginated.return_value = ([vessel_response_mock()], 1)
    app.dependency_overrides[get_vessel_service] = lambda: mock_service

    response = await client.get("/api/v1/vessels/")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["total"] == 1


@pytest.mark.asyncio
async def test_update_vessel_success(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.update_vessel.return_value = vessel_response_mock(status="maintenance")
    app.dependency_overrides[get_vessel_service] = lambda: mock_service

    response = await client.put("/api/v1/vessels/1", json={"status": "maintenance"})
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["status"] == "maintenance"


@pytest.mark.asyncio
async def test_update_vessel_not_found(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.update_vessel.return_value = None
    app.dependency_overrides[get_vessel_service] = lambda: mock_service

    response = await client.put("/api/v1/vessels/999", json={"status": "inactive"})
    app.dependency_overrides.clear()
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_vessel_success(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.delete_vessel.return_value = True
    app.dependency_overrides[get_vessel_service] = lambda: mock_service

    response = await client.delete("/api/v1/vessels/1")
    app.dependency_overrides.clear()
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_vessel_not_found(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.delete_vessel.return_value = False
    app.dependency_overrides[get_vessel_service] = lambda: mock_service

    response = await client.delete("/api/v1/vessels/999")
    app.dependency_overrides.clear()
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_vessel_by_name_found(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_vessel_by_name.return_value = vessel_response_mock(name="Titan")
    app.dependency_overrides[get_vessel_service] = lambda: mock_service

    response = await client.get("/api/v1/vessels/search/by-name?name=Titan")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["name"] == "Titan"


@pytest.mark.asyncio
async def test_search_vessel_by_name_not_found(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_vessel_by_name.return_value = None
    app.dependency_overrides[get_vessel_service] = lambda: mock_service

    response = await client.get("/api/v1/vessels/search/by-name?name=Unknown")
    app.dependency_overrides.clear()
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_vessels_by_status(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_vessels_by_status.return_value = [
        vessel_response_mock(status="active")
    ]
    app.dependency_overrides[get_vessel_service] = lambda: mock_service

    response = await client.get("/api/v1/vessels/search/by-status?status=active")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_vessels_by_location(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_vessels_by_location.return_value = [
        vessel_response_mock(current_location="Port A")
    ]
    app.dependency_overrides[get_vessel_service] = lambda: mock_service

    response = await client.get("/api/v1/vessels/search/by-location?location=Port A")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()[0]["current_location"] == "Port A"


@pytest.mark.asyncio
async def test_available_vessels(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_available_vessels.return_value = [
        vessel_response_mock(capacity_weight=70000.0)
    ]
    app.dependency_overrides[get_vessel_service] = lambda: mock_service

    response = await client.get("/api/v1/vessels/search/available?min_capacity=10000")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()[0]["capacity_weight"] >= 10000
