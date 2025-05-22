from datetime import datetime

import pytest
from pydantic import ValidationError
from app.api.schemas.vessel_schema import VesselCreate


def valid_vessel_data():
    return {
        "name": "Ever Given",
        "capacity_weight": 200000,
        "year_built": 2018,
        "status": "active",
        "max_speed": 22.5,
        "current_location": "Rotterdam",
    }


def test_vessel_create_valid() -> None:
    vessel = VesselCreate(**valid_vessel_data())
    assert vessel.name == "Ever Given"


def test_status_invalid() -> None:
    data = valid_vessel_data()
    data["status"] = "broken"
    with pytest.raises(ValidationError):
        VesselCreate(**data)


def test_blank_name_fails() -> None:
    data = valid_vessel_data()
    data["name"] = "   "
    with pytest.raises(ValidationError):
        VesselCreate(**data)


def test_blank_location_fails() -> None:
    data = valid_vessel_data()
    data["current_location"] = ""
    with pytest.raises(ValidationError):
        VesselCreate(**data)


def test_year_built_too_future() -> None:
    from datetime import datetime

    data = valid_vessel_data()
    data["year_built"] = datetime.now().year + 5
    with pytest.raises(ValidationError):
        VesselCreate(**data)


def test_year_built_min_and_max() -> None:
    data = valid_vessel_data()
    data["year_built"] = 1900
    VesselCreate(**data)
    max_year = datetime.now().year + 2
    data["year_built"] = max_year
    VesselCreate(**data)
    data["year_built"] = max_year + 1
    with pytest.raises(ValidationError):
        VesselCreate(**data)


def test_max_speed_negative() -> None:
    data = valid_vessel_data()
    data["max_speed"] = -1
    with pytest.raises(ValidationError):
        VesselCreate(**data)


def test_capacity_weight_negative() -> None:
    data = valid_vessel_data()
    data["capacity_weight"] = -100
    with pytest.raises(ValidationError):
        VesselCreate(**data)


def test_optional_fields() -> None:
    data = valid_vessel_data()
    data["year_built"] = None
    data["max_speed"] = None
    data["capacity_weight"] = None
    vessel = VesselCreate(**data)
    assert vessel.year_built is None
    assert vessel.max_speed is None
    assert vessel.capacity_weight is None
