import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from app.api.schemas.cargo_schema import CargoResponse, CargoStatus, CargoSummary
from app.main import app
from app.dependency import get_cargo_service


@pytest.mark.asyncio
async def test_create_cargo_success(client: AsyncClient) -> None:
    # Mock response from the service
    mock_response = CargoResponse(
        id=1,
        contract_id=123,
        weight=100.0,
        status=CargoStatus.PENDING.value,
        destination="Lisbon",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # AsyncMock simulating service with desired behavior
    mock_service = AsyncMock()
    mock_service.create_cargo.return_value = mock_response

    # Override FastAPI dependency
    app.dependency_overrides[get_cargo_service] = lambda: mock_service

    # Act
    response = await client.post(
        "/api/v1/cargo/",
        json={
            "contract_id": 123,
            "weight": 100.0,
            "customs_status": "pending",
            "destination": "Lisbon",
        },
    )

    # Clean override after test
    app.dependency_overrides.clear()

    # Assert
    assert response.status_code == 201
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_get_cargo_found(client: AsyncClient) -> None:
    mock_response = CargoResponse(
        id=1,
        contract_id=123,
        weight=100.0,
        status=CargoStatus.PENDING.value,
        destination="Lisbon",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    with patch(
        "app.api.routes.v1.endpoints.cargo_endpoint.get_cargo_service"
    ) as mock_dep:
        mock_service = AsyncMock()
        mock_service.get_cargo.return_value = mock_response
        mock_dep.return_value = mock_service
        app.dependency_overrides[get_cargo_service] = lambda: mock_service

        response = await client.get("/api/v1/cargo/1")

        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_get_cargo_not_found(client: AsyncClient) -> None:
    with patch(
        "app.api.routes.v1.endpoints.cargo_endpoint.get_cargo_service"
    ) as mock_dep:
        mock_service = AsyncMock()
        mock_service.get_cargo.return_value = None
        mock_dep.return_value = mock_service
        app.dependency_overrides[get_cargo_service] = lambda: mock_service
        response = await client.get("/api/v1/cargo/999")
        app.dependency_overrides.clear()
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_cargo_success(client: AsyncClient) -> None:
    with patch(
        "app.api.routes.v1.endpoints.cargo_endpoint.get_cargo_service"
    ) as mock_dep:
        mock_service = AsyncMock()
        mock_service.update_cargo.return_value = CargoResponse(
            id=1,
            contract_id=1,
            weight=200.0,
            status=CargoStatus.IN_TRANSIT.value,
            destination="Porto",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mock_dep.return_value = mock_service
        app.dependency_overrides[get_cargo_service] = lambda: mock_service
        response = await client.put(
            "/api/v1/cargo/1",
            json={"weight": 200.0, "status": "in_transit", "destination": "Porto"},
        )

        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert response.json()["status"] == "in_transit"


@pytest.mark.asyncio
async def test_update_cargo_not_found(client: AsyncClient) -> None:
    with patch(
        "app.api.routes.v1.endpoints.cargo_endpoint.get_cargo_service"
    ) as mock_dep:
        mock_service = AsyncMock()
        mock_service.update_cargo.return_value = None
        mock_dep.return_value = mock_service
        app.dependency_overrides[get_cargo_service] = lambda: mock_service
        response = await client.put("/api/v1/cargo/999", json={"status": "delivered"})
        app.dependency_overrides.clear()
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_cargo_success(client: AsyncClient) -> None:
    with patch(
        "app.api.routes.v1.endpoints.cargo_endpoint.get_cargo_service"
    ) as mock_dep:
        mock_service = AsyncMock()
        mock_service.delete_cargo.return_value = True
        mock_dep.return_value = mock_service
        app.dependency_overrides[get_cargo_service] = lambda: mock_service
        response = await client.delete("/api/v1/cargo/1")
        app.dependency_overrides.clear()
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_cargo_not_found(client: AsyncClient) -> None:
    with patch(
        "app.api.routes.v1.endpoints.cargo_endpoint.get_cargo_service"
    ) as mock_dep:
        mock_service = AsyncMock()
        mock_service.delete_cargo.return_value = False
        mock_dep.return_value = mock_service
        app.dependency_overrides[get_cargo_service] = lambda: mock_service
        response = await client.delete("/api/v1/cargo/999")
        app.dependency_overrides.clear()
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_cargos_success(client: AsyncClient) -> None:
    with patch(
        "app.api.routes.v1.endpoints.cargo_endpoint.get_cargo_service"
    ) as mock_dep:
        mock_service = AsyncMock()
        mock_service.get_cargoes_paginated.return_value = (
            [
                CargoResponse(
                    id=1,
                    contract_id=1,
                    status=CargoStatus.PENDING.value,
                    destination="Lisbon",
                    cargo_type="Electronics",
                    weight=100.0,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            ],
            1,
        )
        mock_dep.return_value = mock_service
        app.dependency_overrides[get_cargo_service] = lambda: mock_service

        response = await client.get("/api/v1/cargo/")

        app.dependency_overrides.clear()
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] == 1


@pytest.mark.asyncio
async def test_list_cargos_success_empty(client: AsyncClient) -> None:
    with patch(
        "app.api.routes.v1.endpoints.cargo_endpoint.get_cargo_service"
    ) as mock_dep:
        mock_service = AsyncMock()
        mock_service.get_cargoes_paginated.return_value = ([], 0)
        mock_dep.return_value = mock_service
        app.dependency_overrides[get_cargo_service] = lambda: mock_service
        response = await client.get("/api/v1/cargo/")
        app.dependency_overrides.clear()
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_cargo_with_tracking(client: AsyncClient) -> None:
    mock_response = CargoResponse(
        id=1,
        contract_id=1,
        weight=100.0,
        status=CargoStatus.IN_TRANSIT.value,
        destination="Lisbon",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    with patch(
        "app.api.routes.v1.endpoints.cargo_endpoint.get_cargo_service"
    ) as mock_dep:
        mock_service = AsyncMock()
        mock_service.get_cargo_with_tracking.return_value = mock_response
        mock_dep.return_value = mock_service
        app.dependency_overrides[get_cargo_service] = lambda: mock_service

        response = await client.get("/api/v1/cargo/1/with-tracking")

        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_get_cargoes_by_contract(client: AsyncClient) -> None:
    mock_response = [
        CargoResponse(
            id=1,
            contract_id=1,
            weight=100.0,
            status=CargoStatus.PENDING.value,
            destination="Lisbon",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    ]

    with patch(
        "app.api.routes.v1.endpoints.cargo_endpoint.get_cargo_service"
    ) as mock_dep:
        mock_service = AsyncMock()
        mock_service.get_cargoes_by_contract.return_value = mock_response
        mock_dep.return_value = mock_service
        app.dependency_overrides[get_cargo_service] = lambda: mock_service

        response = await client.get("/api/v1/cargo/search/by-contract/1")

        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert response.json()[0]["contract_id"] == 1


@pytest.mark.asyncio
async def test_get_cargoes_by_status(client: AsyncClient) -> None:
    mock_response = [
        CargoResponse(
            id=2,
            contract_id=2,
            weight=150.0,
            status=CargoStatus.DELIVERED.value,
            destination="Porto",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    ]

    with patch(
        "app.api.routes.v1.endpoints.cargo_endpoint.get_cargo_service"
    ) as mock_dep:
        mock_service = AsyncMock()
        mock_service.get_cargoes_by_status.return_value = mock_response
        mock_dep.return_value = mock_service
        app.dependency_overrides[get_cargo_service] = lambda: mock_service

        response = await client.get("/api/v1/cargo/search/by-status?status=delivered")

        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert all(item["status"] == "delivered" for item in response.json())


@pytest.mark.asyncio
async def test_get_cargoes_by_destination(client: AsyncClient) -> None:
    mock_response = [
        CargoResponse(
            id=3,
            contract_id=3,
            weight=120.0,
            status=CargoStatus.PENDING.value,
            destination="Lisbon",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    ]

    with patch(
        "app.api.routes.v1.endpoints.cargo_endpoint.get_cargo_service"
    ) as mock_dep:
        mock_service = AsyncMock()
        mock_service.get_cargoes_by_destination.return_value = mock_response
        mock_dep.return_value = mock_service
        app.dependency_overrides[get_cargo_service] = lambda: mock_service

        response = await client.get(
            "/api/v1/cargo/search/by-destination?destination=Lisbon"
        )

        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert all(item["destination"] == "Lisbon" for item in response.json())
