import pytest
from unittest.mock import AsyncMock
from types import SimpleNamespace
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.services.client_service import ClientService
from app.api.schemas.client_schema import ClientCreate, ClientUpdate, ClientResponse


@pytest.mark.asyncio
async def test_create_client_success() -> None:
    mock_repo = AsyncMock()
    service = ClientService(mock_repo)
    client_data = ClientCreate(
        company_name="ServiceTest",
        contact_email="service@teste.com",
        tax_id="123456789",
    )
    expected_response = ClientResponse(
        id=1,
        company_name="ServiceTest",
        contact_email="service@teste.com",
        tax_id="123456789",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )

    mock_repo.find_by_email.return_value = None
    mock_repo.find_by_tax_id.return_value = None
    mock_repo.create.return_value = expected_response

    result = await service.create_client(client_data)
    assert result == expected_response
    mock_repo.find_by_email.assert_called_once_with("service@teste.com")
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_client_duplicate_email() -> None:
    mock_repo = AsyncMock()
    service = ClientService(mock_repo)
    client_data = ClientCreate(
        company_name="ServiceTest", contact_email="dup@teste.com", tax_id="123456789"
    )
    mock_repo.find_by_email.return_value = client_data

    with pytest.raises(ValueError, match="already exists"):
        await service.create_client(client_data)


@pytest.mark.asyncio
async def test_create_client_tax_id_already_registered() -> None:
    mock_repo = AsyncMock()
    service = ClientService(mock_repo)
    client_data = ClientCreate(
        company_name="ServiceTest", contact_email="test@teste.com", tax_id="123456789"
    )
    mock_repo.find_by_email.return_value = None
    mock_repo.find_by_tax_id.return_value = SimpleNamespace(**client_data.model_dump())

    with pytest.raises(ValueError, match="already registered"):
        await service.create_client(client_data)


@pytest.mark.asyncio
async def test_create_client_integrity_error() -> None:
    mock_repo = AsyncMock()
    service = ClientService(mock_repo)
    client_data = ClientCreate(
        company_name="ServiceTest", contact_email="err@teste.com", tax_id="123456789"
    )
    mock_repo.find_by_email.return_value = None
    mock_repo.find_by_tax_id.return_value = None
    mock_repo.create.side_effect = IntegrityError(
        "UNIQUE constraint failed: client.tax_id", {}, None
    )

    with pytest.raises(ValueError, match="Tax ID must be unique"):
        await service.create_client(client_data)


@pytest.mark.asyncio
async def test_update_client_success() -> None:
    mock_repo = AsyncMock()
    service = ClientService(mock_repo)
    old = ClientResponse(
        id=1,
        company_name="Old",
        contact_email="old@a.com",
        tax_id="123456789",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )
    updated = ClientResponse(
        id=1,
        company_name="Old",
        contact_email="new@a.com",
        tax_id="123456789",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T01:00:00",
    )
    update_data = ClientUpdate(contact_email="new@a.com")

    mock_repo.get_by_id.return_value = old
    mock_repo.find_by_email.return_value = None
    mock_repo.update.return_value = updated

    result = await service.update_client(1, update_data)
    assert result.contact_email == "new@a.com"


@pytest.mark.asyncio
async def test_delete_client() -> None:
    mock_repo = AsyncMock()
    service = ClientService(mock_repo)
    mock_repo.delete.return_value = True
    result = await service.delete_client(1)
    assert result is True


# ---------- EXTRAS DE COBERTURA ----------
@pytest.mark.asyncio
async def test_create_client_invalid_email() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(company_name="X", contact_email="notanemail", tax_id="123456789")


@pytest.mark.asyncio
async def test_update_client_email_in_use() -> None:
    mock_repo = AsyncMock()
    service = ClientService(mock_repo)
    old = ClientResponse(
        id=1,
        company_name="Old",
        contact_email="old@a.com",
        tax_id="123456789",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )
    another = ClientResponse(
        id=2,
        company_name="Other",
        contact_email="other@a.com",
        tax_id="987654321",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )
    mock_repo.get_by_id.return_value = old
    mock_repo.find_by_email.return_value = another
    update_data = ClientUpdate(contact_email="other@a.com")
    with pytest.raises(ValueError, match="Email already in us"):
        await service.update_client(1, update_data)
