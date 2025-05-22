from datetime import datetime

import pytest
from app.api.schemas.client_schema import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientSummary,
)
from pydantic import ValidationError

# ---------- ClientCreate ----------


def test_client_create_minimal():
    schema = ClientCreate(company_name="Empresa XPTO", contact_email="user@email.com")
    assert schema.company_name == "Empresa XPTO"
    assert schema.active is True  # default


def test_client_create_full():
    schema = ClientCreate(
        company_name="Teste",
        contact_email="t@t.com",
        contact_phone="123456789",
        address="Rua X",
        tax_id="123236789",
        industry="Logística",
        active=False,
        credit_limit=1000.50,
        payment_terms="30 days",
    )
    assert schema.contact_phone == "123456789"
    assert schema.credit_limit == 1000.50


def test_client_create_invalid_email() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(company_name="X", contact_email="bad-email")


def test_client_create_negative_credit_limit() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(company_name="X", contact_email="x@x.com", credit_limit=-10)


def test_client_create_company_name_too_short() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(company_name="", contact_email="x@x.com")


def test_client_create_phone_too_long() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(company_name="X", contact_email="x@x.com", contact_phone="1" * 21)


# ---------- ClientUpdate ----------


def test_client_update_at_least_one() -> None:
    schema = ClientUpdate(company_name="Novo Nome")
    assert schema.company_name == "Novo Nome"


def test_client_update_all_fields() -> None:
    schema = ClientUpdate(
        company_name="Alterado",
        contact_email="novo@email.com",
        contact_phone="8888",
        address="Nova rua",
        tax_id="456",
        industry="Transporte",
        active=False,
        credit_limit=5,
        payment_terms="60 days",
    )
    assert schema.payment_terms == "60 days"


def test_client_update_empty_fails() -> None:
    with pytest.raises(ValueError) as exc:
        ClientUpdate()
    assert "At least one field must be updated" in str(exc.value)


def test_client_update_invalid_email() -> None:
    with pytest.raises(ValidationError):
        ClientUpdate(contact_email="email-invalido")


def test_client_update_negative_credit_limit() -> None:
    with pytest.raises(ValidationError):
        ClientUpdate(credit_limit=-500)


def test_client_update_long_address() -> None:
    with pytest.raises(ValidationError):
        ClientUpdate(address="x" * 512)


# ---------- ClientResponse ----------


def test_client_response_inherits() -> None:
    resp = ClientResponse(
        id=1,
        company_name="RespTest",
        contact_email="r@t.com",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert resp.id == 1


# ---------- ClientSummary ----------


def test_client_summary_basic() -> None:
    summary = ClientSummary(
        id=99, company_name="Sum", contact_email="sum@a.com", active=True
    )
    assert summary.company_name == "Sum"


def test_client_create_invalid_tax_id_alpha() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(company_name="A", contact_email="a@b.com", tax_id="abc123xyz")


def test_client_create_invalid_tax_id_short() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(company_name="A", contact_email="a@b.com", tax_id="1234567")


def test_client_create_valid_tax_id() -> None:
    client = ClientCreate(company_name="B", contact_email="b@c.com", tax_id="123456789")
    assert client.tax_id == "123456789"


# --- Contact phone validation ---


def test_client_create_phone_with_letters() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(
            company_name="A", contact_email="a@b.com", contact_phone="12345ABCD"
        )


def test_client_create_phone_only_digits() -> None:
    client = ClientCreate(
        company_name="C", contact_email="c@d.com", contact_phone="912345678"
    )
    assert client.contact_phone == "912345678"


# --- Payment terms validation ---


def test_client_create_payment_terms_invalid() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(company_name="A", contact_email="a@b.com", payment_terms="60dias")


def test_client_create_payment_terms_valid() -> None:
    client = ClientCreate(
        company_name="A", contact_email="a@b.com", payment_terms="30 days"
    )
    assert client.payment_terms == "30 days"


# --- Credit limit maximum validation ---


def test_client_create_credit_limit_too_high() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(company_name="A", contact_email="a@b.com", credit_limit=20_000_000)


def test_client_create_credit_limit_max_ok() -> None:
    client = ClientCreate(
        company_name="A", contact_email="a@b.com", credit_limit=5_000_000
    )
    assert client.credit_limit == 5_000_000


# --- Company name only spaces ---


def test_client_create_company_name_spaces() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(company_name="     ", contact_email="a@b.com")


# --- Trim whitespace ---


def test_client_create_company_name_trims() -> None:
    client = ClientCreate(company_name="   Teste Ltda  ", contact_email="t@t.com")
    assert client.company_name == "Teste Ltda"


def test_client_create_address_trims() -> None:
    client = ClientCreate(
        company_name="B", contact_email="b@c.com", address="   Rua XPTO   "
    )
    assert client.address == "Rua XPTO"


# --- All at once valid ---


def test_client_create_all_valid():
    client = ClientCreate(
        company_name="Good",
        contact_email="good@abc.com",
        contact_phone="987654321",
        tax_id="123456789",
        credit_limit=80000,
        payment_terms="30 days",
        address="Rua Final",
        industry="Logística",
    )
    assert client.company_name == "Good"
    assert client.tax_id == "123456789"
    assert client.credit_limit == 80000
