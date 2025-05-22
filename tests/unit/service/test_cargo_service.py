import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.api.schemas.cargo_schema import (
    CargoCreate,
    CargoUpdate,
    CargoResponse,
    CargoSummary,
)
from app.domain.enums.status import CargoStatus

# ---------------------
# helper valid data
# ---------------------


def valid_cargo_data():
    return {
        "contract_id": 1,
        "actual_departure": datetime(2024, 6, 1, 8, 0),
        "estimated_arrival": datetime(2024, 6, 2, 8, 0),
        "actual_arrival": datetime(2024, 6, 2, 7, 0),
        "weight": 1000.0,
        "dimensions": "10x10x10",
        "insurance_value": 5000.0,
        "customs_status": CargoStatus.PENDING.value,
        "cargo_type": "Container",
        "destination": "Lisbon",
    }


# ---------------------
# Test CargoCreate
# ---------------------


def test_cargo_create_valid() -> None:
    data = valid_cargo_data()
    obj = CargoCreate(**data)
    assert obj.contract_id == 1
    assert obj.status == CargoStatus.PENDING.value


def test_cargo_create_invalid_status() -> None:
    data = valid_cargo_data()
    data["status"] = "not_a_status"
    with pytest.raises(ValidationError) as exc:
        CargoCreate(**data)
    assert "Status must be one of" in str(exc.value)


def test_cargo_create_negative_weight() -> None:
    data = valid_cargo_data()
    data["weight"] = -10
    with pytest.raises(ValidationError):
        CargoCreate(**data)


def test_cargo_create_invalid_dimensions() -> None:
    data = valid_cargo_data()
    data["dimensions"] = "x" * 60  # Mais de 50 caracteres
    with pytest.raises(ValidationError):
        CargoCreate(**data)


def test_cargo_create_insurance_value_negative() -> None:
    data = valid_cargo_data()
    data["insurance_value"] = -1
    with pytest.raises(ValidationError):
        CargoCreate(**data)


def test_cargo_create_arrival_before_departure() -> None:
    data = valid_cargo_data()
    data["actual_arrival"] = data["actual_departure"] - timedelta(hours=1)
    with pytest.raises(ValidationError) as exc:
        CargoCreate(**data)
    assert "Actual arrival must be after actual departure" in str(exc.value)


def test_cargo_create_empty_optional_fields() -> None:
    data = valid_cargo_data()
    data["dimensions"] = None
    data["insurance_value"] = None
    data["cargo_type"] = None
    data["destination"] = None
    obj = CargoCreate(**data)
    assert obj.dimensions is None


# ---------------------
# Test CargoUpdate
# ---------------------


def test_cargo_update_valid() -> None:
    data = {"weight": 100, "status": CargoStatus.IN_TRANSIT.value}
    obj = CargoUpdate(**data)
    assert obj.weight == 100
    assert obj.status == CargoStatus.IN_TRANSIT.value


def test_cargo_update_all_fields_empty() -> None:
    with pytest.raises(ValidationError) as exc:
        CargoUpdate()
    assert "At least one field must be updated" in str(exc.value)


def test_cargo_update_invalid_customs_status() -> None:
    data = {"status": "WRONG_STATUS"}
    with pytest.raises(ValidationError) as exc:
        CargoUpdate(**data)
    assert "Status must be one of" in str(exc.value)


def test_cargo_update_invalid_weight():
    data = {"weight": -5}
    with pytest.raises(ValidationError):
        CargoUpdate(**data)


def test_cargo_update_invalid_dimensions() -> None:
    data = {"dimensions": "x" * 55}
    with pytest.raises(ValidationError):
        CargoUpdate(**data)


# ---------------------
# Test de Response/Summary
# ---------------------


def test_cargo_response_inherits() -> None:
    data = valid_cargo_data()
    data["id"] = 123
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = datetime.utcnow()
    obj = CargoResponse(**data)
    assert obj.id == 123


def test_cargo_summary() -> None:
    obj = CargoSummary(
        id=1,
        contract_id=1,
        cargo_type="Bulk",
        status=CargoStatus.PENDING.value,
        destination="Tokyo",
        weight=500.0,
    )
    assert obj.cargo_type == "Bulk"
