from typing import Any, AsyncGenerator, Coroutine

from httpx import AsyncClient, ASGITransport
from pytest_asyncio import fixture
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.domain.models.base import Base
from app.domain.models.vessel import Vessel
from app.domain.models.cargo import Cargo
from app.main import app

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@fixture
async def session() -> AsyncGenerator[Any, Any]:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        yield session
    await engine.dispose()


@fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@fixture
async def sample_vessel(session) -> Vessel:
    vessel = Vessel(
        id=1,
        name="Fixture Vessel",
        capacity_weight=1000,
        current_location="Porto",
        status="active",
    )
    session.add(vessel)
    await session.commit()
    await session.refresh(vessel)
    return vessel


@fixture
async def sample_cargo(session, sample_vessel) -> Cargo:
    cargo = Cargo(id=1, contract_id=1, status="pending", destination="Lisbon")
    session.add(cargo)
    await session.commit()
    await session.refresh(cargo)
    return cargo
