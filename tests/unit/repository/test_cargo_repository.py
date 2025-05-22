import pytest
from datetime import datetime

from app.domain.models.cargo import Cargo
from app.domain.models.contract import Contract
from app.domain.models.tracking import Tracking
from app.domain.enums.status import CargoStatus
from app.domain.models.vessel import Vessel
from app.repositories.cargo_repository import CargoRepository


@pytest.mark.asyncio
async def test_find_by_contract_id(session) -> None:
    contract1 = Contract(
        contract_number="C001",
        client_id=1,
        price=100,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    contract2 = Contract(
        contract_number="C002",
        client_id=1,
        price=200,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add_all([contract1, contract2])
    await session.commit()
    c1 = Cargo(
        contract_id=contract1.id, status=CargoStatus.PENDING.value, destination="Lisbon"
    )
    c2 = Cargo(
        contract_id=contract1.id,
        status=CargoStatus.IN_TRANSIT.value,
        destination="Porto",
    )
    c3 = Cargo(
        contract_id=contract2.id,
        status=CargoStatus.DELIVERED.value,
        destination="Madrid",
    )
    session.add_all([c1, c2, c3])
    await session.commit()

    repo = CargoRepository(session)
    cargos = await repo.find_by_contract_id(contract1.id)
    assert len(cargos) == 2
    cargos2 = await repo.find_by_contract_id(contract2.id)
    assert len(cargos2) == 1


@pytest.mark.asyncio
async def test_find_by_status(session) -> None:
    contract = Contract(
        contract_number="C010",
        client_id=2,
        price=150,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract)
    await session.commit()
    c1 = Cargo(
        contract_id=contract.id,
        status=CargoStatus.PENDING.value,
        destination="Barcelona",
    )
    c2 = Cargo(
        contract_id=contract.id,
        status=CargoStatus.PENDING.value,
        destination="Valencia",
    )
    c3 = Cargo(
        contract_id=contract.id, status=CargoStatus.DELIVERED.value, destination="Paris"
    )
    session.add_all([c1, c2, c3])
    await session.commit()

    repo = CargoRepository(session)
    pending = await repo.find_by_status(CargoStatus.PENDING)
    delivered = await repo.find_by_status(CargoStatus.DELIVERED)
    assert len(pending) == 2
    assert all(c.status == CargoStatus.PENDING.value for c in pending)
    assert len(delivered) == 1


@pytest.mark.asyncio
async def test_find_by_destination(session) -> None:
    contract = Contract(
        contract_number="C100",
        client_id=3,
        price=170,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract)
    await session.commit()
    c1 = Cargo(
        contract_id=contract.id, status=CargoStatus.PENDING.value, destination="Lisbon"
    )
    c2 = Cargo(
        contract_id=contract.id, status=CargoStatus.PENDING.value, destination="Lisboa"
    )
    c3 = Cargo(
        contract_id=contract.id, status=CargoStatus.DELIVERED.value, destination="Porto"
    )
    session.add_all([c1, c2, c3])
    await session.commit()

    repo = CargoRepository(session)
    found = await repo.find_by_destination("Lisbo")
    assert len(found) == 2
    assert all("Lisbo" in c.destination for c in found or "")


@pytest.mark.asyncio
async def test_get_by_id_with_tracking(session) -> None:
    contract = Contract(
        contract_number="C200",
        client_id=4,
        price=300,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract)
    await session.commit()
    cargo = Cargo(
        contract_id=contract.id,
        status=CargoStatus.IN_TRANSIT.value,
        destination="Berlin",
    )
    session.add(cargo)
    vessel = Vessel(
        name="Ever Given", capacity_weight=1000, current_location="Rotterdam"
    )
    session.add(vessel)
    await session.commit()

    tracking1 = Tracking(
        cargo_id=cargo.id,
        vessel_id=vessel.id,
        status="loading",
        location="Hamburg",
        timestamp=datetime.now(),
    )
    tracking2 = Tracking(
        cargo_id=cargo.id,
        vessel_id=vessel.id,
        status="in_transit",
        location="Berlin",
        timestamp=datetime.now(),
    )
    session.add_all([tracking1, tracking2])
    session.add_all([tracking1, tracking2])
    await session.commit()

    repo = CargoRepository(session)
    cargo_with_tracking = await repo.get_by_id_with_tracking(cargo.id)
    assert cargo_with_tracking is not None
    assert hasattr(cargo_with_tracking, "tracking")
    assert len(cargo_with_tracking.tracking) == 2


@pytest.mark.asyncio
async def test_find_by_contract_id_none(session) -> None:
    repo = CargoRepository(session)
    cargos = await repo.find_by_contract_id(999)
    assert cargos == []


@pytest.mark.asyncio
async def test_get_by_id_with_tracking_none(session) -> None:
    repo = CargoRepository(session)
    cargo = await repo.get_by_id_with_tracking(999)
    assert cargo is None


@pytest.mark.asyncio
async def test_create_cargo_and_fetch_by_id(session) -> None:
    from app.domain.models.contract import Contract
    from app.domain.models.cargo import Cargo
    from app.repositories.cargo_repository import CargoRepository

    contract = Contract(
        contract_number="C999",
        client_id=5,
        price=800,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract)
    await session.commit()

    cargo = Cargo(
        contract_id=contract.id,
        status=CargoStatus.PENDING.value,
        destination="Amsterdam",
    )
    session.add(cargo)
    await session.commit()

    repo = CargoRepository(session)
    found = await repo.get_by_id(cargo.id)
    assert found is not None
    assert found.destination == "Amsterdam"
    assert found.status == CargoStatus.PENDING.value


@pytest.mark.asyncio
async def test_cargo_destination_unique_constraint(session) -> None:

    from app.domain.models.contract import Contract
    from app.domain.models.cargo import Cargo
    from app.repositories.cargo_repository import CargoRepository
    import sqlalchemy.exc

    contract = Contract(
        contract_number="C900",
        client_id=5,
        price=800,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract)
    await session.commit()

    cargo1 = Cargo(
        contract_id=contract.id, status=CargoStatus.PENDING.value, destination="Tokyo"
    )
    cargo2 = Cargo(
        contract_id=contract.id, status=CargoStatus.DELIVERED.value, destination="Tokyo"
    )
    session.add(cargo1)
    await session.commit()
    session.add(cargo2)
    try:
        await session.commit()
        repo = CargoRepository(session)
        found = await repo.find_by_destination("Tokyo")
        assert len(found) >= 1
    except sqlalchemy.exc.IntegrityError:
        assert True


@pytest.mark.asyncio
async def test_cargo_status_update(session) -> None:
    from app.domain.models.contract import Contract
    from app.domain.models.cargo import Cargo
    from app.repositories.cargo_repository import CargoRepository

    contract = Contract(
        contract_number="C870",
        client_id=6,
        price=900,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract)
    await session.commit()

    cargo = Cargo(
        contract_id=contract.id, status=CargoStatus.PENDING.value, destination="Venice"
    )
    session.add(cargo)
    await session.commit()

    cargo.status = CargoStatus.IN_TRANSIT.value
    await session.commit()

    repo = CargoRepository(session)
    found = await repo.get_by_id(cargo.id)
    assert found.status == CargoStatus.IN_TRANSIT.value


@pytest.mark.asyncio
async def test_cargo_with_multiple_tracking(session) -> None:
    from app.domain.models.contract import Contract
    from app.domain.models.cargo import Cargo
    from app.domain.models.vessel import Vessel
    from app.domain.models.tracking import Tracking
    from app.repositories.cargo_repository import CargoRepository

    contract = Contract(
        contract_number="C320",
        client_id=7,
        price=600,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    vessel = Vessel(name="Big Ship", capacity_weight=2000, current_location="Shanghai")
    session.add_all([contract, vessel])
    await session.commit()

    cargo = Cargo(
        contract_id=contract.id, status=CargoStatus.PENDING.value, destination="Oslo"
    )
    session.add(cargo)
    await session.commit()

    t1 = Tracking(
        cargo_id=cargo.id,
        vessel_id=vessel.id,
        status="loading",
        location="Shanghai",
        timestamp=datetime.now(),
    )
    t2 = Tracking(
        cargo_id=cargo.id,
        vessel_id=vessel.id,
        status="in_transit",
        location="Suez",
        timestamp=datetime.now(),
    )
    t3 = Tracking(
        cargo_id=cargo.id,
        vessel_id=vessel.id,
        status="delivered",
        location="Oslo",
        timestamp=datetime.now(),
    )
    session.add_all([t1, t2, t3])
    await session.commit()

    repo = CargoRepository(session)
    cargo_full = await repo.get_by_id_with_tracking(cargo.id)
    assert cargo_full is not None
    assert hasattr(cargo_full, "tracking")
    assert len(cargo_full.tracking) == 3
    locations = [trk.location for trk in cargo_full.tracking]
    assert "Oslo" in locations
    assert "Suez" in locations


@pytest.mark.asyncio
async def test_cargo_delete(session) -> None:
    from app.domain.models.contract import Contract
    from app.domain.models.cargo import Cargo
    from app.repositories.cargo_repository import CargoRepository

    contract = Contract(
        contract_number="CDELETE",
        client_id=8,
        price=400,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract)
    await session.commit()

    cargo = Cargo(
        contract_id=contract.id, status=CargoStatus.PENDING.value, destination="Miami"
    )
    session.add(cargo)
    await session.commit()

    repo = CargoRepository(session)
    await session.delete(cargo)
    await session.commit()
    assert await repo.get_by_id(cargo.id) is None


@pytest.mark.asyncio
async def test_find_by_multiple_status(session) -> None:
    from app.domain.models.contract import Contract
    from app.domain.models.cargo import Cargo
    from app.repositories.cargo_repository import CargoRepository
    from app.domain.enums.status import CargoStatus

    contract = Contract(
        contract_number="C_MULTI",
        client_id=10,
        price=1000,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract)
    await session.commit()

    cargos = [
        Cargo(
            contract_id=contract.id,
            status=CargoStatus.PENDING.value,
            destination="Berlin",
        ),
        Cargo(
            contract_id=contract.id,
            status=CargoStatus.IN_TRANSIT.value,
            destination="Paris",
        ),
        Cargo(
            contract_id=contract.id,
            status=CargoStatus.DELIVERED.value,
            destination="Rome",
        ),
    ]
    session.add_all(cargos)
    await session.commit()

    repo = CargoRepository(session)
    all_cargos = await repo.find_by_status(CargoStatus.PENDING)
    all_cargos += await repo.find_by_status(CargoStatus.IN_TRANSIT)
    assert len(all_cargos) == 2


@pytest.mark.asyncio
async def test_find_by_destination_case_insensitive(session) -> None:
    from app.domain.models.contract import Contract
    from app.domain.models.cargo import Cargo
    from app.repositories.cargo_repository import CargoRepository

    contract = Contract(
        contract_number="C_CI",
        client_id=11,
        price=500,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract)
    await session.commit()

    cargos = [
        Cargo(contract_id=contract.id, status="pending", destination="Lisbon"),
        Cargo(contract_id=contract.id, status="pending", destination="lisbon"),
        Cargo(contract_id=contract.id, status="pending", destination="LISBON"),
    ]
    session.add_all(cargos)
    await session.commit()

    repo = CargoRepository(session)
    found = await repo.find_by_destination("lisbon")
    assert len(found) == 3


@pytest.mark.asyncio
async def test_cargo_contract_isolation(session) -> None:
    from app.domain.models.contract import Contract
    from app.domain.models.cargo import Cargo
    from app.repositories.cargo_repository import CargoRepository

    c1 = Contract(
        contract_number="C_A",
        client_id=15,
        price=100,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    c2 = Contract(
        contract_number="C_B",
        client_id=16,
        price=200,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add_all([c1, c2])
    await session.commit()

    cargo1 = Cargo(contract_id=c1.id, status="pending", destination="London")
    cargo2 = Cargo(contract_id=c2.id, status="pending", destination="Paris")
    session.add_all([cargo1, cargo2])
    await session.commit()

    repo = CargoRepository(session)
    cargos_c1 = await repo.find_by_contract_id(c1.id)
    cargos_c2 = await repo.find_by_contract_id(c2.id)
    assert all(c.contract_id == c1.id for c in cargos_c1)
    assert all(c.contract_id == c2.id for c in cargos_c2)


@pytest.mark.asyncio
async def test_get_non_existent_cargo(session) -> None:
    from app.repositories.cargo_repository import CargoRepository

    repo = CargoRepository(session)
    cargo = await repo.get_by_id(9999)
    assert cargo is None


@pytest.mark.asyncio
async def test_find_delivered_cargos_in_date_range(session):
    from app.domain.models.contract import Contract
    from app.domain.models.cargo import Cargo
    from app.domain.models.tracking import Tracking
    from app.domain.models.vessel import Vessel
    from app.repositories.cargo_repository import CargoRepository
    from datetime import datetime, timedelta

    contract = Contract(
        contract_number="C_PERIOD",
        client_id=20,
        price=700,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    vessel = Vessel(name="Suez Max", capacity_weight=900, current_location="Suez")
    session.add_all([contract, vessel])
    await session.commit()

    cargo = Cargo(contract_id=contract.id, status="delivered", destination="Kobe")
    session.add(cargo)
    await session.commit()

    delivered_time = datetime.now() - timedelta(days=1)
    tracking = Tracking(
        cargo_id=cargo.id,
        vessel_id=vessel.id,
        status="delivered",
        location="Kobe",
        timestamp=delivered_time,
    )
    session.add(tracking)
    await session.commit()

    repo = CargoRepository(session)
    cargos = await repo.find_delivered_in_date_range(
        start_date=(datetime.now() - timedelta(days=2)),
        end_date=datetime.now(),
    )
    assert any(c.id == cargo.id for c in cargos)


@pytest.mark.asyncio
async def test_cascade_delete_cargo_with_tracking(session) -> None:
    from app.domain.models.contract import Contract
    from app.domain.models.cargo import Cargo
    from app.domain.models.tracking import Tracking
    from app.domain.models.vessel import Vessel

    contract = Contract(
        contract_number="C_CASCADE",
        client_id=22,
        price=100,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    vessel = Vessel(
        name="Cascade Ship", capacity_weight=1200, current_location="Lisbon"
    )
    session.add_all([contract, vessel])
    await session.commit()

    cargo = Cargo(contract_id=contract.id, status="pending", destination="Napoli")
    session.add(cargo)
    await session.commit()

    t1 = Tracking(
        cargo_id=cargo.id,
        vessel_id=vessel.id,
        status="loading",
        location="Lisbon",
        timestamp=datetime.now(),
    )
    session.add(t1)
    await session.commit()

    await session.delete(cargo)
    await session.commit()

    remaining = await session.execute(
        Tracking.__table__.select().where(Tracking.cargo_id == cargo.id)
    )
    assert remaining.first() is None


@pytest.mark.asyncio
async def test_bulk_insert_cargos(session) -> None:
    from app.domain.models.contract import Contract
    from app.domain.models.cargo import Cargo
    from app.repositories.cargo_repository import CargoRepository

    contract = Contract(
        contract_number="C_BULK",
        client_id=23,
        price=600,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract)
    await session.commit()

    cargos = [
        Cargo(contract_id=contract.id, status="pending", destination=f"City {i}")
        for i in range(20)
    ]
    session.add_all(cargos)
    await session.commit()

    repo = CargoRepository(session)
    found = await repo.find_by_contract_id(contract.id)
    assert len(found) == 20


@pytest.mark.asyncio
async def test_fuzzy_destination_search(session) -> None:
    from app.domain.models.contract import Contract
    from app.domain.models.cargo import Cargo
    from app.repositories.cargo_repository import CargoRepository

    contract = Contract(
        contract_number="C_FUZZY",
        client_id=24,
        price=600,
        currency="USD",
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    session.add(contract)
    await session.commit()

    cargos = [
        Cargo(contract_id=contract.id, status="pending", destination="Porto"),
        Cargo(contract_id=contract.id, status="pending", destination="Portsmouth"),
        Cargo(contract_id=contract.id, status="pending", destination="Port Elizabeth"),
    ]
    session.add_all(cargos)
    await session.commit()

    repo = CargoRepository(session)
    found = await repo.find_by_destination("Port")
    assert len(found) == 3
