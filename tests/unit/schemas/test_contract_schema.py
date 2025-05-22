import pytest
from pydantic import ValidationError
from datetime import datetime, timedelta
from app.api.schemas.contract_schema import ContractCreate


def valid_contract_data():
    return {
        "contract_number": "CT-123",
        "client_id": 1,
        "price": 5000.00,
        "currency": "USD",
        "start_date": datetime(2024, 1, 1),
        "end_date": datetime(2024, 2, 1),
        "payment_terms": "30 days",
        "insurance_coverage": 2000,
        "incoterms": "FOB",
        "status": "pending",
        "notes": "Valid contract",
    }


def test_contract_valid() -> None:
    data = valid_contract_data()
    contract = ContractCreate(**data)
    assert contract.contract_number == "CT-123"


def test_end_date_before_start_date_fails() -> None:
    data = valid_contract_data()
    data["end_date"] = data["start_date"] - timedelta(days=1)
    with pytest.raises(ValidationError):
        ContractCreate(**data)


def test_invalid_currency_lowercase() -> None:
    data = valid_contract_data()
    data["currency"] = "usd"
    with pytest.raises(ValidationError):
        ContractCreate(**data)


def test_invalid_incoterms() -> None:
    data = valid_contract_data()
    data["incoterms"] = "fake"
    with pytest.raises(ValidationError):
        ContractCreate(**data)


def test_invalid_payment_terms() -> None:
    data = valid_contract_data()
    data["payment_terms"] = "30days"  # missing space
    with pytest.raises(ValidationError):
        ContractCreate(**data)


def test_unrealistic_price() -> None:
    data = valid_contract_data()
    data["price"] = 1_000_000_001
    with pytest.raises(ValidationError):
        ContractCreate(**data)


def test_notes_blank() -> None:
    data = valid_contract_data()
    data["notes"] = "     "
    with pytest.raises(ValidationError):
        ContractCreate(**data)


def test_optional_fields_can_be_none() -> None:
    data = valid_contract_data()
    data["incoterms"] = None
    data["payment_terms"] = None
    data["insurance_coverage"] = None
    contract = ContractCreate(**data)
    assert contract.incoterms is None
    assert contract.payment_terms is None
    assert contract.insurance_coverage is None
