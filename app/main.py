from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.logging_config import setup_logger
from app.core.exception_handlers import ExceptionHandlers
from app.domain.models.base import Base
from app.infrastructure.config import settings
from app.infrastructure.database import engine
from app.infrastructure.seed_data import insert_initial_data
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.routes.v1.endpoints.tracking_endpoint import router as tracking_endpoint
from app.api.routes.v1.endpoints.client_endpoint import router as client_endpoint
from app.api.routes.v1.endpoints.vessel_endpoint import router as vessel_endpoint
from app.api.routes.v1.endpoints.cargo_endpoint import router as cargo_endpoint
from app.api.routes.v1.endpoints.contract_endpoint import router as contract_endpoint

from app.domain.models import client, contract, vessel, cargo, tracking

# Setup logging first
setup_logger()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing application lifespan...")

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSession(engine) as session:
            await insert_initial_data(session)

        logger.info("All tables created and seed data inserted.")
    except Exception as e:
        logger.exception("Error during initialization: %s", e)

    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="v1.0.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(client_endpoint, prefix="/api/v1")
app.include_router(tracking_endpoint, prefix="/api/v1")
app.include_router(vessel_endpoint, prefix="/api/v1")
app.include_router(cargo_endpoint, prefix="/api/v1")
app.include_router(contract_endpoint, prefix="/api/v1")

# Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
ExceptionHandlers.register_handlers(app)
