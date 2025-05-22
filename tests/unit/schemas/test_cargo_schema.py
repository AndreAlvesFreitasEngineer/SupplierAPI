import pytest
from datetime import datetime, timedelta

from app.api.schemas.cargo_schema import CargoCreate, CargoUpdate
from app.domain.enums.status import CargoStatus


def test_cargo_create_minimal() -> None:
    data = {
        "contract_id": 1,
        "weight": 5.0,
        "status": CargoStatus.PENDING.value,
    }
    schema = CargoCreate(**data)
    assert schema.contract_id == 1
    assert schema.weight == 5.0
    assert schema.status == CargoStatus.PENDING.value


# Fail: invalid status
def test_cargo_create_invalid_status() -> None:
    data = {"contract_id": 1, "weight": 5.0, "status": "WRONG_STATUS"}
    with pytest.raises(ValueError) as exc:
        CargoCreate(**data)
    assert "Status must be one of" in str(exc.value)


# Success: arrival after departure
def test_cargo_create_arrival_after_departure() -> None:
    departure = datetime(2024, 1, 1, 10, 0)
    arrival = departure + timedelta(hours=3)
    schema = CargoCreate(
        contract_id=1,
        weight=3,
        status=CargoStatus.PENDING.value,
        actual_departure=departure,
        actual_arrival=arrival,
    )
    assert schema.actual_arrival > schema.actual_departure


# Fail: arrival before departure
def test_cargo_create_arrival_before_departure() -> None:
    departure = datetime(2024, 1, 1, 10, 0)
    arrival = departure - timedelta(hours=3)
    with pytest.raises(ValueError) as exc:
        CargoCreate(
            contract_id=1,
            weight=3,
            status=CargoStatus.PENDING.value,
            actual_departure=departure,
            actual_arrival=arrival,
        )
    assert "Actual arrival must be after actual departure" in str(exc.value)


# Update: must update at least one field
def test_cargo_update_must_update_field() -> None:
    with pytest.raises(ValueError) as exc:
        CargoUpdate()
    assert "At least one field must be updated" in str(exc.value)


# Update: update customs_status with valid
def test_cargo_update_status_ok() -> None:
    schema = CargoUpdate(status=CargoStatus.PENDING.value)
    assert schema.status == CargoStatus.PENDING.value


# Update: update customs_status with invalid
def test_cargo_update_status_invalid() -> None:
    with pytest.raises(ValueError) as exc:
        CargoUpdate(status="UNKNOWN")
    assert "Status must be one of" in str(exc.value)


# Update: updating a field other than customs_status
def test_cargo_update_other_field() -> None:
    schema = CargoUpdate(weight=42.0)
    assert schema.weight == 42.0
