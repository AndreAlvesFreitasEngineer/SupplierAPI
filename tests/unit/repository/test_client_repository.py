import pytest
from sqlalchemy.exc import IntegrityError
from app.domain.models.client import Client
from app.repositories.client_repository import ClientRepository


@pytest.mark.asyncio
async def test_find_by_email(session) -> None:
    repo = ClientRepository(session)
    client = Client(company_name="RepoTest", contact_email="repo@teste.com")
    session.add(client)
    await session.commit()
    result = await repo.find_by_email("repo@teste.com")
    assert result is not None
    assert result.company_name == "RepoTest"


@pytest.mark.asyncio
async def test_find_by_email_not_found(session) -> None:
    repo = ClientRepository(session)
    result = await repo.find_by_email("notfound@teste.com")
    assert result is None


@pytest.mark.asyncio
async def test_find_by_email_empty(session) -> None:
    repo = ClientRepository(session)
    result = await repo.find_by_email("")
    assert result is None


@pytest.mark.asyncio
async def test_find_by_name(session) -> None:
    repo = ClientRepository(session)
    client1 = Client(company_name="Alpha Shipping", contact_email="alpha@ship.com")
    client2 = Client(company_name="Beta Shipping", contact_email="beta@ship.com")
    session.add_all([client1, client2])
    await session.commit()
    results = await repo.find_by_name("Shipping")
    assert len(results) == 2
    results = await repo.find_by_name("Alpha")
    assert len(results) == 1
    assert results[0].company_name == "Alpha Shipping"


@pytest.mark.asyncio
async def test_find_by_name_not_found(session) -> None:
    repo = ClientRepository(session)
    results = await repo.find_by_name("Nonexistent")
    assert results == []


@pytest.mark.asyncio
async def test_find_by_tax_id(session) -> None:
    repo = ClientRepository(session)
    client = Client(
        company_name="Taxed Client", contact_email="tax@client.com", tax_id="TAX123"
    )
    session.add(client)
    await session.commit()
    result = await repo.find_by_tax_id("TAX123")
    assert result is not None
    assert result.tax_id == "TAX123"


@pytest.mark.asyncio
async def test_find_by_tax_id_not_found(session) -> None:
    repo = ClientRepository(session)
    result = await repo.find_by_tax_id("NOTAX")
    assert result is None


@pytest.mark.asyncio
async def test_get_paginated(session):
    """Test pagination functionality with various page sizes."""
    repo = ClientRepository(session)

    # Setup test data
    test_clients = [
        Client(company_name=f"Client{i}", contact_email=f"c{i}@mail.com")
        for i in range(10)
    ]
    session.add_all(test_clients)
    await session.commit()

    # Test case 1: page_size=0 should return empty list but correct total count
    results, total = await repo.get_paginated(page=5, page_size=0)
    assert results == []
    assert total == 10

    # Test case 2: Normal pagination
    results2, total2 = await repo.get_paginated(page=1, page_size=5)
    assert len(results2) == 5
    assert total2 == 10

    # Verify the first 5 clients are returned
    all_names = [c.company_name for c in results2]
    for i in range(5):
        assert f"Client{i}" in all_names

    # Test case 3: Verify second page contains the remaining items
    results3, total3 = await repo.get_paginated(page=2, page_size=5)
    assert len(results3) == 5
    assert total3 == 10
    assert all(c.company_name not in all_names for c in results3)


@pytest.mark.asyncio
async def test_get_paginated_empty(session) -> None:
    repo = ClientRepository(session)
    results, total = await repo.get_paginated(page=5, page_size=0)
    assert results == []
    assert total == 0


@pytest.mark.asyncio
async def test_count(session) -> None:
    repo = ClientRepository(session)
    for i in range(3):
        session.add(
            Client(company_name=f"CountClient{i}", contact_email=f"count{i}@mail.com")
        )
    await session.commit()
    count = await repo.count()
    assert count == 3


@pytest.mark.asyncio
async def test_count_empty(session):
    repo = ClientRepository(session)
    count = await repo.count()
    assert count == 0


@pytest.mark.asyncio
async def test_credit_limit_negative(session) -> None:
    bad_client = Client(
        company_name="Bad Credit", contact_email="bad@teste.com", credit_limit=-500
    )
    session.add(bad_client)
    with pytest.raises(IntegrityError):
        await session.commit()
    await session.rollback()
