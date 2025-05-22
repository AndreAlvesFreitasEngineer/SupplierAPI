import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError
from app.services.vessel_service import VesselService
from app.api.schemas.vessel_schema import VesselCreate, VesselUpdate, VesselResponse
from app.domain.enums.status import VesselStatus
from pydantic import ValidationError
from datetime import datetime


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_repo):
    return VesselService(mock_repo)


def full_vessel_dict(**kwargs):
    data = {
        "id": kwargs.get("id", 1),
        "name": kwargs.get("name", "Barco"),
        "current_location": kwargs.get("current_location", "Porto"),
        "capacity_weight": kwargs.get("capacity_weight", 1234.5),
        "status": kwargs.get("status", "active"),
        "year_built": kwargs.get("year_built", 2000),
        "max_speed": kwargs.get("max_speed", 50.0),
        "created_at": kwargs.get("created_at", datetime.now()),
        "updated_at": kwargs.get("updated_at", datetime.now()),
    }
    return data


@pytest.mark.asyncio
async def test_create_vessel_success(
    service: VesselService, mock_repo: MagicMock
) -> None:
    vessel_data = VesselCreate(
        name="Titanic",
        current_location="Porto",
        capacity_weight=1234.5,
        status="active",
        year_built=2000,
        max_speed=50.0,
    )
    mock_repo.find_by_name.return_value = None
    # DEVOLVE TODOS OS CAMPOS!
    mock_repo.create.return_value = full_vessel_dict(
        name="Titanic", current_location="Porto"
    )
    result = await service.create_vessel(vessel_data)
    assert result.name == "Titanic"
    assert result.current_location == "Porto"


@pytest.mark.asyncio
async def test_create_vessel_duplicate_name(
    service: VesselService, mock_repo: MagicMock
) -> None:
    vessel_data = VesselCreate(name="Santa Maria", current_location="Lisboa")
    mock_repo.find_by_name.return_value = vessel_data.model_dump() | {"id": 1}
    with pytest.raises(ValueError, match="already exists"):
        await service.create_vessel(vessel_data)


@pytest.mark.asyncio
async def test_create_vessel_integrity_error(
    service: VesselService, mock_repo: MagicMock
) -> None:
    vessel_data = VesselCreate(name="Titanic", current_location="Porto")
    mock_repo.find_by_name.return_value = None
    mock_repo.create.side_effect = IntegrityError("err", {}, None)
    with pytest.raises(ValueError, match="Database integrity error"):
        await service.create_vessel(vessel_data)


@pytest.mark.asyncio
async def test_create_vessel_invalid_status() -> None:
    with pytest.raises(ValidationError):
        VesselCreate(name="Test", current_location="Porto", status="invalid-status")


@pytest.mark.asyncio
async def test_get_vessel(service: VesselService, mock_repo: MagicMock) -> None:
    vessel = full_vessel_dict(id=1, name="Lusitania", current_location="Porto")
    mock_repo.get_by_id.return_value = vessel
    result = await service.get_vessel(1)
    assert result.id == 1
    assert result.name == "Lusitania"


@pytest.mark.asyncio
async def test_get_vessel_not_found(
    service: VesselService, mock_repo: MagicMock
) -> None:
    mock_repo.get_by_id.return_value = None
    result = await service.get_vessel(123)
    assert result is None


@pytest.mark.asyncio
async def test_update_vessel_success(
    service: VesselService, mock_repo: MagicMock
) -> None:
    vessel_id = 1
    old = full_vessel_dict(id=vessel_id, name="A", current_location="Lisboa")
    updated = old | {"name": "B"}
    mock_repo.get_by_id.return_value = old
    mock_repo.find_by_name.return_value = None
    mock_repo.update.return_value = updated
    update_data = VesselUpdate(name="B")
    result = await service.update_vessel(vessel_id, update_data)
    assert result.name == "B"


@pytest.mark.asyncio
async def test_update_vessel_not_found(
    service: VesselService, mock_repo: MagicMock
) -> None:
    mock_repo.get_by_id.return_value = None
    update_data = VesselUpdate(name="Nao")
    result = await service.update_vessel(99, update_data)
    assert result is None


@pytest.mark.asyncio
async def test_update_vessel_integrity_error(
    service: VesselService, mock_repo: MagicMock
) -> None:
    vessel_id = 1
    old = full_vessel_dict(id=vessel_id, name="A", current_location="Lisboa")
    mock_repo.get_by_id.return_value = old
    mock_repo.find_by_name.return_value = None
    mock_repo.update.side_effect = IntegrityError("err", {}, None)
    with pytest.raises(ValueError, match="Database integrity error"):
        await service.update_vessel(vessel_id, VesselUpdate(name="B"))


@pytest.mark.asyncio
async def test_delete_vessel(service: VesselService, mock_repo: MagicMock) -> None:
    mock_repo.delete.return_value = True
    assert await service.delete_vessel(1) is True


@pytest.mark.asyncio
async def test_get_vessel_by_name(service: VesselService, mock_repo: MagicMock) -> None:
    vessel = full_vessel_dict(id=10, name="Azores", current_location="Funchal")
    mock_repo.find_by_name.return_value = vessel
    result = await service.get_vessel_by_name("Azores")
    assert result.name == "Azores"
    assert result.current_location == "Funchal"


@pytest.mark.asyncio
async def test_get_vessels_by_status(
    service: VesselService, mock_repo: MagicMock
) -> None:
    vessels = [
        full_vessel_dict(
            id=1, status=VesselStatus.ACTIVE.value, name="A", current_location="Lisbon"
        ),
        full_vessel_dict(
            id=2, status=VesselStatus.ACTIVE.value, name="B", current_location="Porto"
        ),
    ]
    mock_repo.find_by_status.return_value = vessels
    result = await service.get_vessels_by_status(VesselStatus.ACTIVE.value)
    assert all([v.status == VesselStatus.ACTIVE.value for v in result])


@pytest.mark.asyncio
async def test_get_available_vessels(
    service: VesselService, mock_repo: MagicMock
) -> None:
    mock_repo.find_available_vessels.return_value = [
        full_vessel_dict(id=1, capacity_weight=2000.0, name="A", current_location="X"),
        full_vessel_dict(id=2, capacity_weight=3000.0, name="B", current_location="Y"),
    ]
    result = await service.get_available_vessels(min_capacity=1000)
    assert result[0].capacity_weight == 2000.0


@pytest.mark.asyncio
async def test_get_vessels_by_location(
    service: VesselService, mock_repo: MagicMock
) -> None:
    vessels = [full_vessel_dict(id=1, current_location="Lisbon", name="A")]
    mock_repo.find_by_location.return_value = vessels
    result = await service.get_vessels_by_location("Lisbon")
    assert result[0].current_location == "Lisbon"


# Edge case: Name cannot be blank or only spaces
def test_vessel_create_blank_name() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        VesselCreate(name="   ", current_location="Lisbon")


# Edge case: Year built far in future
def test_vessel_create_future_year_built() -> None:
    from pydantic import ValidationError
    from datetime import datetime

    this_year = datetime.now().year
    with pytest.raises(ValidationError):
        VesselCreate(name="Barco", current_location="Porto", year_built=this_year + 5)
