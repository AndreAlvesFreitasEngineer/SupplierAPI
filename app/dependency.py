from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter

from app.infrastructure.database import SessionLocal
from app.repositories.cargo_repository import CargoRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.tracking_repository import TrackingRepository
from app.repositories.vessel_repository import VesselRepository
from app.services.cargo_service import CargoService
from app.services.client_service import ClientService
from app.services.contract_service import ContractService
from app.services.tracking_service import TrackingService
from app.services.vessel_service import VesselService


async def get_db() -> AsyncSession:
    """Database session dependency with proper cleanup"""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_vessel_service(db: AsyncSession = Depends(get_db)) -> VesselService:
    return VesselService(VesselRepository(db))


async def get_client_service(db: AsyncSession = Depends(get_db)) -> ClientService:
    return ClientService(ClientRepository(db))


async def get_tracking_service(db: AsyncSession = Depends(get_db)) -> TrackingService:
    return TrackingService(TrackingRepository(db))


async def get_cargo_service(db: AsyncSession = Depends(get_db)) -> CargoService:
    return CargoService(CargoRepository(db))


async def get_contract_service(db: AsyncSession = Depends(get_db)) -> ContractService:
    return ContractService(ContractRepository(db))


async def get_rate_limiter(request: Request):
    """Enhanced rate limiting with proxy support"""
    return RateLimiter(
        times=1000,
        seconds=60,
        identifier=lambda req: req.headers.get("X-Forwarded-For", req.client.host),
    )
