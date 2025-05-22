import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from app.services.tracking_service import TrackingService
from app.domain.enums.status import TrackingStatus
from app.api.schemas.tracking_schema import (
    TrackingCreate,
    TrackingUpdate,
    TrackingResponse,
    TrackingHistoryResponse,
)


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_repo):
    return TrackingService(mock_repo)


@pytest.fixture
def fake_tracking_response():
    return {
        "id": 1,
        "cargo_id": 1,
        "vessel_id": 2,
        "status": TrackingStatus.LOADING.value,
        "location": "Port",
        "timestamp": datetime.now(),
        "notes": None,
        "temperature": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def fake_history_response():
    return {
        "id": 1,
        "tracking_id": 1,
        "previous_status": "pending",
        "new_status": TrackingStatus.LOADING.value,
        "previous_location": "Old Port",
        "new_location": "Port",
        "timestamp": datetime.now(),
        "created_at": datetime.now(),
        "cargo_id": 1,
        "vessel_id": 2,
        "updated_at": datetime.now(),
    }


@pytest.mark.asyncio
async def test_create_tracking(service, mock_repo, fake_tracking_response) -> None:
    data = TrackingCreate(
        cargo_id=1,
        vessel_id=2,
        status=TrackingStatus.LOADING.value,
        location="Port",
        timestamp=datetime.now(),
    )
    mock_repo.create_with_history.return_value = fake_tracking_response
    result = await service.create_tracking(data)
    assert isinstance(result, TrackingResponse)
    assert result.cargo_id == 1
    mock_repo.create_with_history.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_tracking_found(service, mock_repo, fake_tracking_response) -> None:
    mock_repo.get_by_id.return_value = fake_tracking_response
    result = await service.get_tracking(1)
    assert isinstance(result, TrackingResponse)
    assert result.id == 1
    mock_repo.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_tracking_not_found(service, mock_repo) -> None:
    mock_repo.get_by_id.return_value = None
    result = await service.get_tracking(999)
    assert result is None
    mock_repo.get_by_id.assert_awaited_once_with(999)


@pytest.mark.asyncio
async def test_get_all_tracking(service, mock_repo, fake_tracking_response) -> None:
    mock_repo.get_all.return_value = [fake_tracking_response]
    result = await service.get_all_tracking()
    assert isinstance(result, list)
    assert isinstance(result[0], TrackingResponse)
    mock_repo.get_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_tracking_success(service, mock_repo) -> None:
    fake_result = {
        "id": 1,
        "cargo_id": 1,
        "vessel_id": 2,
        "status": TrackingStatus.IN_TRANSIT.value,
        "location": "Port",
        "timestamp": datetime.now(),
        "notes": "In transit",
        "temperature": 5.0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    mock_repo.update_with_history.return_value = fake_result

    data = TrackingUpdate(
        status=TrackingStatus.IN_TRANSIT.value,
        timestamp=fake_result["timestamp"],
        notes=fake_result["notes"],
        temperature=fake_result["temperature"],
    )
    result = await service.update_tracking(1, data)
    assert result is not None
    assert result.status == TrackingStatus.IN_TRANSIT.value
    assert result.notes == "In transit"


@pytest.mark.asyncio
async def test_update_tracking_not_found(service, mock_repo) -> None:
    mock_repo.update_with_history.return_value = None
    data = TrackingUpdate(
        status=TrackingStatus.IN_TRANSIT.value,
        timestamp=datetime.now(),
        notes="not found",
        temperature=3.0,
    )
    result = await service.update_tracking(999, data)
    assert result is None


@pytest.mark.asyncio
async def test_delete_tracking(service, mock_repo) -> None:
    mock_repo.delete.return_value = True
    result = await service.delete_tracking(1)
    assert result is True
    mock_repo.delete.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_tracking_by_cargo(
    service, mock_repo, fake_tracking_response
) -> None:
    mock_repo.find_by_cargo_id.return_value = [fake_tracking_response]
    result = await service.get_tracking_by_cargo(1)
    assert isinstance(result, list)
    assert isinstance(result[0], TrackingResponse)
    mock_repo.find_by_cargo_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_tracking_by_vessel(
    service, mock_repo, fake_tracking_response
) -> None:
    mock_repo.find_by_vessel_id.return_value = [fake_tracking_response]
    result = await service.get_tracking_by_vessel(2)
    assert isinstance(result, list)
    assert isinstance(result[0], TrackingResponse)
    mock_repo.find_by_vessel_id.assert_awaited_once_with(2)


@pytest.mark.asyncio
async def test_get_latest_tracking_by_cargo_found(
    service, mock_repo, fake_tracking_response
) -> None:
    mock_repo.find_latest_by_cargo_id.return_value = fake_tracking_response
    result = await service.get_latest_tracking_by_cargo(1)
    assert isinstance(result, TrackingResponse)
    mock_repo.find_latest_by_cargo_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_latest_tracking_by_cargo_not_found(service, mock_repo) -> None:
    mock_repo.find_latest_by_cargo_id.return_value = None
    result = await service.get_latest_tracking_by_cargo(2)
    assert result is None
    mock_repo.find_latest_by_cargo_id.assert_awaited_once_with(2)


@pytest.mark.asyncio
async def test_get_tracking_history(service, mock_repo, fake_history_response) -> None:
    mock_repo.get_tracking_history.return_value = [fake_history_response]
    result = await service.get_tracking_history(1)
    assert isinstance(result, list)
    assert isinstance(result[0], TrackingHistoryResponse)
    mock_repo.get_tracking_history.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_cargoes_by_tracking_status(
    service, mock_repo, fake_tracking_response
) -> None:
    mock_repo.find_cargoes_by_status.return_value = [fake_tracking_response]
    result = await service.get_cargoes_by_tracking_status(TrackingStatus.LOADING)
    assert isinstance(result, list)
    assert isinstance(result[0], TrackingResponse)
    mock_repo.find_cargoes_by_status.assert_awaited_once_with(TrackingStatus.LOADING)


@pytest.mark.asyncio
async def test_get_paginated_tracking_success() -> None:
    mock_repo = AsyncMock()
    mock_repo.count.return_value = 1
    service = TrackingService(mock_repo)
    fake_tracking = {
        "id": 1,
        "cargo_id": 10,
        "vessel_id": 20,
        "status": "loading",
        "location": "Lisbon",
        "timestamp": "2025-05-21T12:00:00",
        "notes": None,
        "temperature": 10.0,
        "created_at": "2025-05-21T12:00:00",
        "updated_at": "2025-05-21T12:00:00",
    }
    mock_repo.get_paginated.return_value = ([fake_tracking], 1)

    items, total = await service.get_paginated(page=1, page_size=10)

    assert total == 1
    assert isinstance(items, list)
    assert items[0].id == 1
    assert items[0].location == "Lisbon"
    mock_repo.get_paginated.assert_awaited_once_with(1, 10, None)


@pytest.mark.asyncio
async def test_get_paginated_tracking_empty() -> None:
    mock_repo = AsyncMock()
    service = TrackingService(mock_repo)
    mock_repo.get_paginated.return_value = ([], 0)

    items, total = await service.get_paginated(page=2, page_size=5)

    assert items == []
    assert total == 0
    mock_repo.get_paginated.assert_awaited_once_with(2, 5, None)
