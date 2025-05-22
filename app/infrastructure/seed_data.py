# app/infrastructure/seed_data.py

from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.client import Client
from app.domain.models.contract import Contract
from app.domain.models.vessel import Vessel
from app.domain.models.cargo import Cargo
from app.domain.models.tracking import Tracking, TrackingHistory
from app.domain.enums.status import (
    ContractStatus,
    CargoStatus,
    VesselStatus,
    TrackingStatus,
)


async def insert_initial_data(session: AsyncSession):
    # Prevent duplicate seeding
    result = await session.execute(select(Client).limit(1))
    if result.scalars().first():
        return

    today = datetime.utcnow().date()

    for i in range(1, 6):  # 5 entries
        # CLIENT
        client = Client(
            company_name=f"Client {i}",
            contact_email=f"client{i}@example.com",
            tax_id=f"TAX-{1000+i}",
            contact_phone=f"+1-555-{1000+i}",
            address=f"{i} Industrial Ave, Metropolis",
            industry="Logistics",
            credit_limit=100000.0 * i,
            payment_terms="30 days",
        )
        session.add(client)
        await session.flush()

        # CONTRACT
        contract = Contract(
            contract_number=f"CNTR-2025-{i:03}",
            client_id=client.id,
            price=50000.0 * i,
            currency="USD",
            start_date=today,
            end_date=today + timedelta(days=90),
            payment_terms="Net 30",
            insurance_coverage=10000.0 * i,
            incoterms="FOB",
            status=ContractStatus.ACTIVE.value,
            notes=f"Contract {i} details...",
        )
        session.add(contract)
        await session.flush()

        # VESSEL
        vessel = Vessel(
            name=f"Vessel-{i}",
            capacity_weight=50000.0 + (i * 10000),
            year_built=2010 + i,
            status=VesselStatus.ACTIVE,
            max_speed=20 + i,
            current_location="Port of Hamburg",
        )
        session.add(vessel)
        await session.flush()

        # CARGO
        cargo = Cargo(
            contract_id=contract.id,
            actual_departure=datetime.utcnow() - timedelta(days=3),
            estimated_arrival=datetime.utcnow() + timedelta(days=7),
            actual_arrival=None,
            weight=5000.0 * i,
            dimensions=f"{i*10}x{i*5}x{i*2}",
            insurance_value=12000.0,
            status=CargoStatus.IN_TRANSIT.value,
            cargo_type="Machinery",
            destination="Port of Singapore",
        )
        session.add(cargo)
        await session.flush()

        # TRACKING
        tracking = Tracking(
            cargo_id=cargo.id,
            vessel_id=vessel.id,
            status=TrackingStatus.IN_TRANSIT.value,
            location="Suez Canal",
            timestamp=datetime.utcnow(),
            notes="Sailing smoothly",
            temperature=19.0 + i,
        )
        session.add(tracking)
        await session.flush()

        # TRACKING HISTORY
        history = TrackingHistory(
            tracking_id=tracking.id,
            cargo_id=cargo.id,
            vessel_id=vessel.id,
            previous_location="Port of Hamburg",
            new_location="Suez Canal",
            previous_status=TrackingStatus.LOADING.value,
            new_status=TrackingStatus.IN_TRANSIT.value,
            changed_at=datetime.utcnow() - timedelta(days=1),
        )
        session.add(history)

    await session.commit()

    # Prevent duplicate seeding
    result = await session.execute(select(Client).limit(1))
    if result.scalars().first():
        return

    # CLIENT
    client = Client(
        company_name="Acme Corp",
        contact_email="info@acme.com",
        tax_id="123456789",
        contact_phone="+1-555-1234",
        address="123 Main Street, Springfield",
        industry="Logistics",
        credit_limit=500000.0,
        payment_terms="30 days",
    )
    session.add(client)
    await session.flush()  # get client.id

    # CONTRACT
    today = datetime.utcnow().date()
    contract = Contract(
        contract_number="ACM-2025-001",
        client_id=client.id,
        price=100000.0,
        currency="USD",
        start_date=today,
        end_date=today + timedelta(days=180),
        payment_terms="Net 30",
        insurance_coverage=20000.0,
        incoterms="FOB",
        status=ContractStatus.ACTIVE.value,
        notes="Standard 6-month logistics agreement.",
    )
    session.add(contract)
    await session.flush()  # get contract.id

    # VESSEL
    vessel = Vessel(
        name="Neptune Carrier",
        capacity_weight=100000.0,
        year_built=2018,
        status=VesselStatus.ACTIVE,
        max_speed=22.5,
        current_location="Port of Rotterdam",
    )
    session.add(vessel)
    await session.flush()  # get vessel.id

    # CARGO
    cargo = Cargo(
        contract_id=contract.id,
        actual_departure=datetime.utcnow() - timedelta(days=3),
        estimated_arrival=datetime.utcnow() + timedelta(days=7),
        actual_arrival=None,
        weight=15000.0,
        dimensions="20x10x5",
        insurance_value=25000.0,
        status=CargoStatus.IN_TRANSIT.value,
        cargo_type="Electronics",
        destination="Port of Singapore",
    )
    session.add(cargo)
    await session.flush()  # get cargo.id

    # TRACKING
    tracking = Tracking(
        cargo_id=cargo.id,
        vessel_id=vessel.id,
        status=TrackingStatus.IN_TRANSIT.value,
        location="Suez Canal",
        timestamp=datetime.utcnow(),
        notes="On schedule",
        temperature=21.5,
    )
    session.add(tracking)
    await session.flush()  # get tracking.id

    # TRACKING HISTORY
    history = TrackingHistory(
        tracking_id=tracking.id,
        cargo_id=cargo.id,
        vessel_id=vessel.id,
        previous_location="Port of Rotterdam",
        new_location="Suez Canal",
        previous_status=TrackingStatus.LOADING.value,
        new_status=TrackingStatus.IN_TRANSIT.value,
        changed_at=datetime.utcnow() - timedelta(days=1),
    )
    session.add(history)

    # Commit all
    await session.commit()
