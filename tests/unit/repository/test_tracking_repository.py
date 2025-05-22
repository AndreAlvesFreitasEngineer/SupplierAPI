import pytest
from datetime import datetime, timedelta

from app.domain.models.tracking import Tracking
from app.domain.enums.status import TrackingStatus
from app.repositories.tracking_repository import TrackingRepository


@pytest.mark.asyncio
async def test_create_tracking_and_find_by_cargo_id(
    session, sample_cargo, sample_vessel
) -> None:
    tracking = Tracking(
        cargo_id=sample_cargo.id,
        vessel_id=sample_vessel.id,
        status=TrackingStatus.LOADING.value,
        location="Lisbon",
        timestamp=datetime.utcnow(),
    )
    session.add(tracking)
    await session.commit()

    repo = TrackingRepository(session)
    found = await repo.find_by_cargo_id(sample_cargo.id)
    assert len(found) == 1
    assert found[0].location == "Lisbon"
    assert found[0].status == TrackingStatus.LOADING.value


@pytest.mark.asyncio
async def test_find_by_vessel_id(session, sample_cargo, sample_vessel) -> None:
    tracking = Tracking(
        cargo_id=sample_cargo.id,
        vessel_id=sample_vessel.id,
        status=TrackingStatus.IN_TRANSIT.value,
        location="Porto",
        timestamp=datetime.utcnow(),
    )
    session.add(tracking)
    await session.commit()

    repo = TrackingRepository(session)
    found = await repo.find_by_vessel_id(sample_vessel.id)
    assert len(found) == 1
    assert found[0].location == "Porto"
    assert found[0].status == TrackingStatus.IN_TRANSIT.value


@pytest.mark.asyncio
async def test_find_latest_by_cargo_id(session, sample_cargo, sample_vessel) -> None:
    t1 = Tracking(
        cargo_id=sample_cargo.id,
        vessel_id=sample_vessel.id,
        status=TrackingStatus.LOADING.value,
        location="A",
        timestamp=datetime.utcnow() - timedelta(hours=2),
    )
    t2 = Tracking(
        cargo_id=sample_cargo.id,
        vessel_id=sample_vessel.id,
        status=TrackingStatus.IN_TRANSIT.value,
        location="B",
        timestamp=datetime.utcnow(),
    )
    session.add_all([t1, t2])
    await session.commit()

    repo = TrackingRepository(session)
    latest = await repo.find_latest_by_cargo_id(sample_cargo.id)
    assert latest.location == "B"
    assert latest.status == TrackingStatus.IN_TRANSIT.value


@pytest.mark.asyncio
async def test_create_with_history(session, sample_cargo, sample_vessel) -> None:
    repo = TrackingRepository(session)
    tracking_data = {
        "cargo_id": sample_cargo.id,
        "vessel_id": sample_vessel.id,
        "status": TrackingStatus.LOADING.value,
        "location": "Initial Port",
        "timestamp": datetime.utcnow(),
    }
    tracking = await repo.create_with_history(tracking_data)
    assert tracking.id is not None

    history = await repo.get_tracking_history(sample_cargo.id)
    assert len(history) == 1
    assert history[0].new_location == "Initial Port"
    assert history[0].new_status == TrackingStatus.LOADING.value


@pytest.mark.asyncio
async def test_update_with_history(session, sample_cargo, sample_vessel) -> None:
    repo = TrackingRepository(session)
    # Cria tracking inicial
    tracking_data = {
        "cargo_id": sample_cargo.id,
        "vessel_id": sample_vessel.id,
        "status": TrackingStatus.LOADING.value,
        "location": "Port X",
        "timestamp": datetime.utcnow(),
    }
    tracking = await repo.create_with_history(tracking_data)

    # Atualiza status e location
    new_data = {"status": TrackingStatus.IN_TRANSIT.value, "location": "Port Y"}
    updated = await repo.update_with_history(tracking.id, new_data)
    assert updated.status == TrackingStatus.IN_TRANSIT.value
    assert updated.location == "Port Y"

    # Histórico deve registrar a mudança
    history = await repo.get_tracking_history(sample_cargo.id)
    assert len(history) == 2
    assert history[-1].previous_location == "Port X"
    assert history[-1].new_location == "Port Y"


@pytest.mark.asyncio
async def test_update_with_history_no_change(
    session, sample_cargo, sample_vessel
) -> None:
    repo = TrackingRepository(session)
    tracking_data = {
        "cargo_id": sample_cargo.id,
        "vessel_id": sample_vessel.id,
        "status": TrackingStatus.LOADING.value,
        "location": "Alpha",
        "timestamp": datetime.utcnow(),
    }
    tracking = await repo.create_with_history(tracking_data)

    await repo.update_with_history(
        tracking.id, {"status": TrackingStatus.LOADING.value, "location": "Alpha"}
    )

    history = await repo.get_tracking_history(sample_cargo.id)
    assert len(history) == 1


@pytest.mark.asyncio
async def test_get_tracking_history(session, sample_cargo, sample_vessel) -> None:
    repo = TrackingRepository(session)
    await repo.create_with_history(
        {
            "cargo_id": sample_cargo.id,
            "vessel_id": sample_vessel.id,
            "status": TrackingStatus.LOADING.value,
            "location": "Port 1",
            "timestamp": datetime.utcnow(),
        }
    )
    await repo.create_with_history(
        {
            "cargo_id": sample_cargo.id,
            "vessel_id": sample_vessel.id,
            "status": TrackingStatus.IN_TRANSIT.value,
            "location": "Port 2",
            "timestamp": datetime.utcnow() + timedelta(hours=1),
        }
    )

    history = await repo.get_tracking_history(sample_cargo.id)
    assert len(history) == 2
    assert history[0].new_location == "Port 1"
    assert history[1].new_location == "Port 2"


@pytest.mark.asyncio
async def test_find_cargoes_by_status(session, sample_cargo, sample_vessel) -> None:
    from app.domain.models.tracking import Tracking

    repo = TrackingRepository(session)
    t1 = Tracking(
        cargo_id=sample_cargo.id,
        vessel_id=sample_vessel.id,
        status=TrackingStatus.LOADING.value,
        location="A",
        timestamp=datetime.utcnow(),
    )
    t2 = Tracking(
        cargo_id=sample_cargo.id,
        vessel_id=sample_vessel.id,
        status=TrackingStatus.DELIVERED.value,
        location="B",
        timestamp=datetime.utcnow(),
    )
    session.add_all([t1, t2])
    await session.commit()
    delivered = await repo.find_cargoes_by_status(TrackingStatus.DELIVERED)
    assert len(delivered) == 1
    assert delivered[0].status == TrackingStatus.DELIVERED.value


@pytest.mark.asyncio
async def test_repository_get_paginated(session) -> None:
    from app.repositories.tracking_repository import TrackingRepository
    from app.domain.models.tracking import Tracking

    repo = TrackingRepository(session)

    for i in range(5):
        tracking = Tracking(
            cargo_id=i + 1,
            vessel_id=i + 1,
            status="loading",
            location=f"Port {i}",
            timestamp=datetime.utcnow(),
            notes=None,
            temperature=15.0 + i,
        )
        session.add(tracking)

    await session.commit()

    items, total = await repo.get_paginated(page=1, page_size=2)
    assert total == 5
    assert len(items) == 2
    assert items[0].location == "Port 0"
    assert items[1].location == "Port 1"

    items, total = await repo.get_paginated(page=2, page_size=2)
    assert total == 5
    assert len(items) == 2
    assert items[0].location == "Port 2"
    assert items[1].location == "Port 3"

    items, total = await repo.get_paginated(page=3, page_size=2)
    assert total == 5
    assert len(items) == 1
    assert items[0].location == "Port 4"

    items, total = await repo.get_paginated(
        page=1, page_size=10, filters={"vessel_id": 3}
    )
    assert total == 1
    assert len(items) == 1
    assert items[0].vessel_id == 3
