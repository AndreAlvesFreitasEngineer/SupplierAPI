import pytest
from datetime import datetime
from unittest.mock import AsyncMock
from httpx import AsyncClient
from app.api.schemas.client_schema import ClientResponse, ClientSummary
from app.main import app
from app.dependency import get_client_service


@pytest.mark.asyncio
async def test_create_client_success(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.create_client.return_value = ClientResponse(
        id=1,
        company_name="Test Co.",
        contact_email="test@example.com",
        contact_phone="123456789",
        address="City",
        tax_id="123456789",
        industry="Tech",
        active=True,
        credit_limit=10000.0,
        payment_terms="30 days",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    app.dependency_overrides[get_client_service] = lambda: mock_service

    response = await client.post(
        "/api/v1/clients/",
        json={
            "company_name": "Test Co.",
            "contact_email": "test@example.com",
            "contact_phone": "123456789",
            "address": "City",
            "tax_id": "123456789",
            "industry": "Tech",
            "active": True,
            "credit_limit": 10000.0,
            "payment_terms": "30 days",
        },
    )
    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["company_name"] == "Test Co."


@pytest.mark.asyncio
async def test_get_client_found(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_client.return_value = ClientResponse(
        id=1,
        company_name="Found Co.",
        contact_email="found@example.com",
        contact_phone="123456789",
        address="Somewhere",
        tax_id="987654321",
        industry="Logistics",
        active=True,
        credit_limit=8000.0,
        payment_terms="45 days",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    app.dependency_overrides[get_client_service] = lambda: mock_service

    response = await client.get("/api/v1/clients/1")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["company_name"] == "Found Co."


@pytest.mark.asyncio
async def test_get_client_not_found(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_client.return_value = None
    app.dependency_overrides[get_client_service] = lambda: mock_service

    response = await client.get("/api/v1/clients/999")
    app.dependency_overrides.clear()
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_client_success(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.update_client.return_value = ClientResponse(
        id=1,
        company_name="Updated Co.",
        contact_email="updated@example.com",
        contact_phone="987654321",
        address="Updated City",
        tax_id="123456789",
        industry="Finance",
        active=False,
        credit_limit=5000.0,
        payment_terms="15 days",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    app.dependency_overrides[get_client_service] = lambda: mock_service

    response = await client.put(
        "/api/v1/clients/1",
        json={"company_name": "Updated Co.", "contact_email": "updated@example.com"},
    )
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["contact_email"] == "updated@example.com"


@pytest.mark.asyncio
async def test_update_client_not_found(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.update_client.return_value = None
    app.dependency_overrides[get_client_service] = lambda: mock_service

    response = await client.put(
        "/api/v1/clients/999", json={"company_name": "NoClient"}
    )
    app.dependency_overrides.clear()
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_client_success(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.delete_client.return_value = True
    app.dependency_overrides[get_client_service] = lambda: mock_service

    response = await client.delete("/api/v1/clients/1")
    app.dependency_overrides.clear()
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_client_not_found(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.delete_client.return_value = False
    app.dependency_overrides[get_client_service] = lambda: mock_service

    response = await client.delete("/api/v1/clients/999")
    app.dependency_overrides.clear()
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_clients_success(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.get_paginated.return_value = (
        [
            ClientSummary(
                id=1,
                company_name="ListClient",
                contact_email="list@example.com",
                active=True,
            )
        ],
        1,
    )
    app.dependency_overrides[get_client_service] = lambda: mock_service

    response = await client.get("/api/v1/clients/")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["total"] == 1


@pytest.mark.asyncio
async def test_search_clients_success(client: AsyncClient) -> None:
    mock_service = AsyncMock()
    mock_service.search_clients_by_name.return_value = [
        ClientSummary(
            id=2,
            company_name="SearchClient",
            contact_email="search@example.com",
            active=True,
        )
    ]
    app.dependency_overrides[get_client_service] = lambda: mock_service

    response = await client.get("/api/v1/clients/search/?name=Search")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()[0]["company_name"] == "SearchClient"
