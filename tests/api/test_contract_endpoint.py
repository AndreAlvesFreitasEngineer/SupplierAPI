import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from app.api.schemas.contract_schema import ContractResponse, ContractStatus
from app.main import app
from app.dependency import get_contract_service


def contract_response_mock(**overrides):
    base = dict(
        id=1,
        contract_number="C-001",
        client_id=1,
        price=1000.0,
        currency="USD",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        status=ContractStatus.ACTIVE.value,
        payment_terms="30 days",
        insurance_coverage=100.0,
        incoterms="FOB",
        notes=None,
    )
    base.update(overrides)
    return ContractResponse(**base)


@pytest.mark.asyncio
async def test_get_contract_found(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_contract.return_value = contract_response_mock()

    app.dependency_overrides[get_contract_service] = lambda: mock_service
    response = await client.get("/api/v1/contracts/1")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_list_contracts_success(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_paginated.return_value = ([contract_response_mock()], 1)

    app.dependency_overrides[get_contract_service] = lambda: mock_service
    response = await client.get("/api/v1/contracts/")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "items" in response.json()


@pytest.mark.asyncio
async def test_update_contract_not_found(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.update_contract.return_value = None

    app.dependency_overrides[get_contract_service] = lambda: mock_service
    response = await client.put("/api/v1/contracts/999", json={"price": 2000})
    app.dependency_overrides.clear()

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_contracts_by_client(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_contracts_by_client.return_value = [
        contract_response_mock(client_id=21)
    ]

    app.dependency_overrides[get_contract_service] = lambda: mock_service
    response = await client.get("/api/v1/contracts/search/by-client/21")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_contracts_by_status(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_contracts_by_status.return_value = [
        contract_response_mock(status=ContractStatus.ACTIVE.value)
    ]

    app.dependency_overrides[get_contract_service] = lambda: mock_service
    response = await client.get("/api/v1/contracts/search/by-status?status=active")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_active_contracts_in_range(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_active_contracts_in_date_range.return_value = [
        contract_response_mock()
    ]

    app.dependency_overrides[get_contract_service] = lambda: mock_service
    response = await client.get(
        "/api/v1/contracts/search/active?start_date=2024-01-01T00:00:00&end_date=2024-12-31T00:00:00"
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert isinstance(response.json(), list)
