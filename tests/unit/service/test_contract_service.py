import pytest
from unittest.mock import AsyncMock
from datetime import date, datetime
from types import SimpleNamespace

from pydantic import ValidationError

from app.services.contract_service import ContractService
from app.api.schemas.contract_schema import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
)
from app.domain.enums.status import ContractStatus


# Fake contract factory
def fake_contract(**kwargs):
    data = dict(
        id=1,
        contract_number="C-010",
        client_id=2,
        price=5000.0,
        currency="USD",
        start_date=date(2024, 6, 1),
        end_date=date(2025, 6, 1),
        status=ContractStatus.ACTIVE.value,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    data.update(kwargs)
    return SimpleNamespace(**data)


@pytest.mark.asyncio
async def test_create_contract_success() -> None:
    mock_repo = AsyncMock()
    mock_repo.find_by_contract_number.return_value = None
    mock_repo.create.return_value = fake_contract()
    service = ContractService(mock_repo)

    contract_data = ContractCreate(
        contract_number="C-010",
        client_id=2,
        price=5000.0,
        currency="USD",
        start_date=date(2024, 6, 1),
        end_date=date(2025, 6, 1),
        status=ContractStatus.ACTIVE.value,
    )

    result = await service.create_contract(contract_data)
    assert isinstance(result, ContractResponse)
    assert result.contract_number == "C-010"
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_contract_duplicate_number() -> None:
    mock_repo = AsyncMock()
    mock_repo.find_by_contract_number.return_value = fake_contract()
    service = ContractService(mock_repo)

    contract_data = ContractCreate(
        contract_number="C-010",
        client_id=2,
        price=5000.0,
        currency="USD",
        start_date=date(2020, 6, 1),
        end_date=date(2026, 6, 1),
        status=ContractStatus.ACTIVE.value,
    )
    with pytest.raises(ValueError, match="Contract number already exists"):
        await service.create_contract(contract_data)


@pytest.mark.asyncio
async def test_create_contract_invalid_dates() -> None:
    with pytest.raises(ValidationError, match="End date must be after start date"):
        ContractCreate(
            contract_number="C-011",
            client_id=2,
            price=1000.0,
            currency="EUR",
            start_date=date(2025, 6, 1),
            end_date=date(2024, 6, 1),
            status=ContractStatus.ACTIVE.value,
        )


@pytest.mark.asyncio
async def test_get_contract_found() -> None:
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = fake_contract()
    service = ContractService(mock_repo)

    contract = await service.get_contract(1)
    assert contract.contract_number == "C-010"
    mock_repo.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_contract_not_found() -> None:
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = None
    service = ContractService(mock_repo)

    contract = await service.get_contract(99)
    assert contract is None


@pytest.mark.asyncio
async def test_update_contract_success() -> None:
    mock_repo = AsyncMock()
    contract_before = fake_contract(contract_number="C-010")
    contract_after = fake_contract(contract_number="C-011")
    mock_repo.get_by_id.return_value = contract_before
    mock_repo.find_by_contract_number.return_value = None
    mock_repo.update.return_value = contract_after
    service = ContractService(mock_repo)

    contract_update = ContractUpdate(
        contract_number="C-011",
        start_date=date(2024, 6, 1),
        end_date=date(2025, 6, 1),
        price=7000.0,
    )
    updated = await service.update_contract(1, contract_update)
    assert updated.contract_number == "C-011"
    mock_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_contract_duplicate_number() -> None:
    mock_repo = AsyncMock()
    contract = fake_contract(contract_number="C-010")
    mock_repo.get_by_id.return_value = contract
    mock_repo.find_by_contract_number.return_value = fake_contract(
        contract_number="C-011"
    )
    service = ContractService(mock_repo)

    contract_update = ContractUpdate(contract_number="C-011")
    with pytest.raises(ValueError, match="Contract number already exists"):
        await service.update_contract(1, contract_update)


@pytest.mark.asyncio
async def test_update_contract_not_found() -> None:
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = None
    service = ContractService(mock_repo)

    contract_update = ContractUpdate(contract_number="C-020")
    updated = await service.update_contract(99, contract_update)
    assert updated is None


@pytest.mark.asyncio
async def test_delete_contract() -> None:
    mock_repo = AsyncMock()
    mock_repo.delete.return_value = True
    service = ContractService(mock_repo)
    result = await service.delete_contract(1)
    assert result is True
    mock_repo.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_contracts_by_client() -> None:
    mock_repo = AsyncMock()
    contracts = [
        fake_contract(client_id=5),
        fake_contract(client_id=5, contract_number="C-012"),
    ]
    mock_repo.find_by_client_id.return_value = contracts
    service = ContractService(mock_repo)
    result = await service.get_contracts_by_client(5)
    assert len(result) == 2
    assert result[0].client_id == 5
    mock_repo.find_by_client_id.assert_called_once_with(5)


@pytest.mark.asyncio
async def test_get_contracts_by_status() -> None:
    mock_repo = AsyncMock()
    contracts = [
        fake_contract(status=ContractStatus.ACTIVE.value),
        fake_contract(status=ContractStatus.ACTIVE.value),
    ]
    mock_repo.find_by_status.return_value = contracts
    service = ContractService(mock_repo)
    result = await service.get_contracts_by_status(ContractStatus.ACTIVE.value)
    assert all(c.status == ContractStatus.ACTIVE.value for c in result)


@pytest.mark.asyncio
async def test_get_active_contracts_in_date_range() -> None:
    mock_repo = AsyncMock()
    contracts = [
        fake_contract(contract_number="C-020"),
        fake_contract(contract_number="C-021"),
    ]
    mock_repo.find_active_in_date_range.return_value = contracts
    service = ContractService(mock_repo)
    start = date(2024, 1, 1)
    end = date(2025, 1, 1)
    result = await service.get_active_contracts_in_date_range(start, end)
    assert len(result) == 2
    mock_repo.find_active_in_date_range.assert_called_once_with(start, end)
