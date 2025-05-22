import pytest
from app.domain.models.vessel import Vessel
from app.domain.enums.status import VesselStatus
from app.repositories.vessel_repository import VesselRepository


@pytest.mark.asyncio
async def test_create_and_find_by_name(session) -> None:
    vessel = Vessel(name="Evergreen", capacity_weight=1500, current_location="Lisbon")
    session.add(vessel)
    await session.commit()

    repo = VesselRepository(session)
    found = await repo.find_by_name("Evergreen")
    assert found is not None
    assert found.name == "Evergreen"


@pytest.mark.asyncio
async def test_find_available_vessels(session) -> None:
    vessel1 = Vessel(
        name="Big1",
        capacity_weight=2000,
        current_location="Rotterdam",
        status=VesselStatus.ACTIVE.value,
    )
    vessel2 = Vessel(
        name="Small1",
        capacity_weight=500,
        current_location="Rotterdam",
        status=VesselStatus.ACTIVE.value,
    )
    vessel3 = Vessel(
        name="NotAvailable",
        capacity_weight=800,
        current_location="Rotterdam",
        status=VesselStatus.INACTIVE.value,
    )
    session.add_all([vessel1, vessel2, vessel3])
    await session.commit()

    repo = VesselRepository(session)
    result = await repo.find_available_vessels(min_capacity=1000)
    assert len(result) == 1
    assert result[0].name == "Big1"


@pytest.mark.asyncio
async def test_find_by_location_case_insensitive(session) -> None:
    vessel1 = Vessel(name="Geo1", capacity_weight=700, current_location="Hamburg")
    vessel2 = Vessel(name="Geo2", capacity_weight=900, current_location="hamburg docks")
    session.add_all([vessel1, vessel2])
    await session.commit()

    repo = VesselRepository(session)
    found = await repo.find_by_location("HAMBURG")
    assert len(found) == 2


@pytest.mark.asyncio
async def test_update_status(session):
    vessel = Vessel(
        name="UpdateTest",
        capacity_weight=1800,
        current_location="Copenhagen",
        status=VesselStatus.ACTIVE.value,
    )
    session.add(vessel)
    await session.commit()

    vessel.status = VesselStatus.MAINTENANCE.value
    await session.commit()

    repo = VesselRepository(session)
    updated = await repo.find_by_name("UpdateTest")
    assert updated.status == VesselStatus.MAINTENANCE.value


@pytest.mark.asyncio
async def test_insert_invalid_status_fails(session) -> None:
    vessel = Vessel(
        name="BadStatus", capacity_weight=1800, current_location="Oslo", status="flying"
    )
    session.add(vessel)
    import sqlalchemy.exc

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        await session.commit()


@pytest.mark.asyncio
async def test_find_vessel_not_found(session) -> None:
    repo = VesselRepository(session)
    found = await repo.find_by_name("DoesNotExist")
    assert found is None


@pytest.mark.asyncio
async def test_find_by_status(session) -> None:
    vessel1 = Vessel(
        name="Voyager",
        capacity_weight=12000,
        current_location="Lisbon",
        status=VesselStatus.ACTIVE.value,
    )
    vessel2 = Vessel(
        name="Horizon",
        capacity_weight=8500,
        current_location="Lisbon",
        status=VesselStatus.MAINTENANCE.value,
    )
    session.add_all([vessel1, vessel2])
    await session.commit()

    repo = VesselRepository(session)
    active_vessels = await repo.find_by_status(VesselStatus.ACTIVE)
    assert len(active_vessels) == 1
    assert active_vessels[0].name == "Voyager"


@pytest.mark.asyncio
async def test_find_available_vessels_by_capacity(session) -> None:
    vessel1 = Vessel(
        name="Atlas",
        capacity_weight=5000,
        current_location="Rotterdam",
        status=VesselStatus.ACTIVE.value,
    )
    vessel2 = Vessel(
        name="Zeus",
        capacity_weight=9000,
        current_location="Rotterdam",
        status=VesselStatus.ACTIVE.value,
    )
    vessel3 = Vessel(
        name="Minerva",
        capacity_weight=3000,
        current_location="Rotterdam",
        status=VesselStatus.INACTIVE.value,
    )
    session.add_all([vessel1, vessel2, vessel3])
    await session.commit()

    repo = VesselRepository(session)
    result = await repo.find_available_vessels(min_capacity=6000)
    assert len(result) == 1
    assert result[0].name == "Zeus"


@pytest.mark.asyncio
async def test_update_vessel_status(session) -> None:
    vessel = Vessel(
        name="UpdateTest",
        capacity_weight=1800,
        current_location="Copenhagen",
        status=VesselStatus.ACTIVE.value,
    )
    session.add(vessel)
    await session.commit()

    vessel.status = VesselStatus.MAINTENANCE.value
    await session.commit()

    repo = VesselRepository(session)
    updated = await repo.find_by_name("UpdateTest")
    assert updated.status == VesselStatus.MAINTENANCE.value


@pytest.mark.asyncio
async def test_update_location_and_capacity(session) -> None:
    vessel = Vessel(
        name="GlobalStar",
        capacity_weight=8000,
        current_location="Genoa",
        status=VesselStatus.ACTIVE.value,
    )
    session.add(vessel)
    await session.commit()

    vessel.current_location = "Barcelona"
    vessel.capacity_weight = 9000
    await session.commit()

    repo = VesselRepository(session)
    found = await repo.find_by_name("GlobalStar")
    assert found.current_location == "Barcelona"
    assert found.capacity_weight == 9000


@pytest.mark.asyncio
async def test_bulk_insert_vessels(session) -> None:
    vessels = [
        Vessel(
            name=f"Vessel{i}",
            capacity_weight=1000 + i * 100,
            current_location="TestPort",
            status=VesselStatus.ACTIVE.value,
        )
        for i in range(10)
    ]
    session.add_all(vessels)
    await session.commit()

    repo = VesselRepository(session)
    found = await repo.find_by_location("TestPort")
    assert len(found) == 10
