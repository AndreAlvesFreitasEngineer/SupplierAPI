import pytest
from datetime import datetime, timedelta
from app.domain.models.contract import Contract
from app.domain.enums.status import ContractStatus
from app.repositories.contract_repository import ContractRepository


@pytest.mark.asyncio
async def test_find_by_client_id(session) -> None:
    repo = ContractRepository(session)
    c1 = Contract(
        contract_number="A1",
        client_id=1,
        price=1000,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        status=ContractStatus.ACTIVE.value,
    )
    c2 = Contract(
        contract_number="A2",
        client_id=1,
        price=2000,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        status=ContractStatus.PENDING.value,
    )
    c3 = Contract(
        contract_number="A3",
        client_id=2,
        price=3000,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        status=ContractStatus.ACTIVE.value,
    )
    session.add_all([c1, c2, c3])
    await session.commit()
    result = await repo.find_by_client_id(1)
    assert len(result) == 2
    result2 = await repo.find_by_client_id(2)
    assert len(result2) == 1


@pytest.mark.asyncio
async def test_find_by_contract_number(session) -> None:
    repo = ContractRepository(session)
    c1 = Contract(
        contract_number="B1",
        client_id=1,
        price=1000,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        status=ContractStatus.ACTIVE.value,
    )
    session.add(c1)
    await session.commit()
    result = await repo.find_by_contract_number("B1")
    assert result is not None
    assert result.contract_number == "B1"
    result404 = await repo.find_by_contract_number("404")
    assert result404 is None


@pytest.mark.asyncio
async def test_find_by_status(session) -> None:
    repo = ContractRepository(session)
    c1 = Contract(
        contract_number="C1",
        client_id=1,
        price=1000,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        status=ContractStatus.PENDING.value,
    )
    c2 = Contract(
        contract_number="C2",
        client_id=1,
        price=1000,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        status=ContractStatus.ACTIVE.value,
    )
    session.add_all([c1, c2])
    await session.commit()
    results = await repo.find_by_status(ContractStatus.ACTIVE)
    assert len(results) == 1
    assert results[0].status == ContractStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_find_active_in_date_range(session) -> None:
    repo = ContractRepository(session)
    today = datetime.now()
    c1 = Contract(
        contract_number="D1",
        client_id=1,
        price=1000,
        currency="USD",
        start_date=today - timedelta(days=5),
        end_date=today + timedelta(days=5),
        status=ContractStatus.ACTIVE.value,
    )
    c2 = Contract(
        contract_number="D2",
        client_id=2,
        price=1000,
        currency="USD",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=20),
        status=ContractStatus.ACTIVE.value,
    )
    c3 = Contract(
        contract_number="D3",
        client_id=1,
        price=1000,
        currency="USD",
        start_date=today - timedelta(days=30),
        end_date=today - timedelta(days=20),
        status=ContractStatus.ACTIVE.value,
    )
    session.add_all([c1, c2, c3])
    await session.commit()
    # Range that only includes c1
    result = await repo.find_active_in_date_range(
        start_date=(today - timedelta(days=1)).date(),
        end_date=(today + timedelta(days=1)).date(),
    )
    assert len(result) == 1
    assert result[0].contract_number == "D1"
    # Range that includes nothing
    result2 = await repo.find_active_in_date_range(
        start_date=(today + timedelta(days=30)).date(),
        end_date=(today + timedelta(days=40)).date(),
    )
    assert len(result2) == 0


@pytest.mark.asyncio
async def test_create_and_find_by_contract_number(session) -> None:
    contract = Contract(
        contract_number="C9999",
        client_id=1,
        price=15000,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=365),
    )
    session.add(contract)
    await session.commit()

    repo = ContractRepository(session)
    found = await repo.find_by_contract_number("C9999")
    assert found is not None
    assert found.price == 15000


@pytest.mark.asyncio
async def test_find_contracts_by_client(session) -> None:
    contract1 = Contract(
        contract_number="C100",
        client_id=11,
        price=900,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    contract2 = Contract(
        contract_number="C101",
        client_id=11,
        price=1300,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    contract3 = Contract(
        contract_number="C102",
        client_id=12,
        price=700,
        currency="EUR",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add_all([contract1, contract2, contract3])
    await session.commit()

    repo = ContractRepository(session)
    contracts = await repo.find_by_client_id(11)
    assert len(contracts) == 2
    numbers = {c.contract_number for c in contracts}
    assert "C100" in numbers and "C101" in numbers


@pytest.mark.asyncio
async def test_find_active_contracts(session) -> None:
    contract1 = Contract(
        contract_number="A1",
        client_id=13,
        price=500,
        currency="USD",
        start_date=datetime.now() - timedelta(days=10),
        end_date=datetime.now() + timedelta(days=10),
    )
    contract2 = Contract(
        contract_number="A2",
        client_id=13,
        price=900,
        currency="USD",
        start_date=datetime.now() - timedelta(days=50),
        end_date=datetime.now() - timedelta(days=5),
    )
    session.add_all([contract1, contract2])
    await session.commit()

    repo = ContractRepository(session)
    active = await repo.find_active_contracts()
    assert any(c.contract_number == "A1" for c in active)
    assert not any(c.contract_number == "A2" for c in active)


@pytest.mark.asyncio
async def test_update_contract_price(session) -> None:
    contract = Contract(
        contract_number="B123",
        client_id=14,
        price=2000,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract)
    await session.commit()

    contract.price = 2500
    await session.commit()

    repo = ContractRepository(session)
    found = await repo.find_by_contract_number("B123")
    assert found.price == 2500


@pytest.mark.asyncio
async def test_delete_contract(session) -> None:
    contract = Contract(
        contract_number="TODELETE",
        client_id=15,
        price=1000,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract)
    await session.commit()

    await session.delete(contract)
    await session.commit()

    repo = ContractRepository(session)
    found = await repo.find_by_contract_number("TODELETE")
    assert found is None


@pytest.mark.asyncio
async def test_unique_contract_number(session) -> None:
    contract1 = Contract(
        contract_number="UNIQUE1",
        client_id=16,
        price=1000,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract1)
    await session.commit()

    contract2 = Contract(
        contract_number="UNIQUE1",
        client_id=17,
        price=1100,
        currency="EUR",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract2)
    import sqlalchemy.exc

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        await session.commit()
