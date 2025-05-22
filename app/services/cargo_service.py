import logging
from typing import List, Optional, Tuple
from sqlalchemy.exc import IntegrityError

from app.domain.enums.status import CargoStatus
from app.repositories.cargo_repository import CargoRepository
from app.api.schemas.cargo_schema import CargoCreate, CargoUpdate, CargoResponse
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class CargoService(BaseService[CargoResponse]):
    def __init__(self, repository: CargoRepository):
        super().__init__(repository)
        self._repository: CargoRepository = repository

    async def create_cargo(self, cargo_data: CargoCreate) -> CargoResponse:
        """
        Cria um novo registro de carga.
        """
        try:
            logger.info(
                "Creating new cargo with contract_id=%s", cargo_data.contract_id
            )
            cargo_dict = cargo_data.model_dump()
            cargo = await self._repository.create(cargo_dict)
            logger.debug("Cargo created: %s", cargo)
            return CargoResponse.model_validate(cargo)
        except IntegrityError as e:
            logger.exception("Integrity error while creating cargo")
            raise ValueError(
                "Failed to create cargo due to data integrity error"
            ) from e

    async def get_cargo(self, cargo_id: int) -> Optional[CargoResponse]:
        """
        Retorna a carga com o ID especificado, se existir.
        """
        logger.info("Fetching cargo with ID %s", cargo_id)
        cargo = await self._repository.get_by_id(cargo_id)
        if cargo:
            logger.debug("Cargo found: %s", cargo)
        else:
            logger.warning("Cargo not found with ID %s", cargo_id)
        return CargoResponse.model_validate(cargo) if cargo else None

    async def get_cargo_with_tracking(self, cargo_id: int) -> Optional[CargoResponse]:
        """
        Retorna a carga com o histórico de tracking incluso.
        """
        logger.info("Fetching cargo with tracking for ID %s", cargo_id)
        cargo = await self._repository.get_by_id_with_tracking(cargo_id)
        if cargo:
            logger.debug("Cargo with tracking found: %s", cargo)
        else:
            logger.warning("No tracking info found for cargo ID %s", cargo_id)
        return CargoResponse.model_validate(cargo) if cargo else None

    async def get_all_cargoes(self) -> List[CargoResponse]:
        """
        Retorna todas as cargas existentes.
        """
        logger.info("Fetching all cargoes")
        cargoes = await self._repository.get_all()
        logger.debug("Total cargoes fetched: %d", len(cargoes))
        return [CargoResponse.model_validate(c) for c in cargoes]

    async def get_cargoes_paginated(
        self, skip: int = 0, limit: int = 100
    ) -> Tuple[List[CargoResponse], int]:
        """
        Retorna uma lista paginada de cargas.
        """
        logger.info("Fetching paginated cargoes: skip=%d, limit=%d", skip, limit)
        cargoes = await self._repository.get_all()
        total = len(cargoes)
        start = min(skip, total)
        end = min(skip + limit, total)
        logger.debug("Returning %d cargoes out of total %d", end - start, total)
        return [CargoResponse.model_validate(c) for c in cargoes[start:end]], total

    async def update_cargo(
        self, cargo_id: int, cargo_data: CargoUpdate
    ) -> Optional[CargoResponse]:
        """
        Atualiza uma carga existente com os dados fornecidos.
        """
        try:
            logger.info("Updating cargo ID %s", cargo_id)
            existing_cargo = await self._repository.get_by_id(cargo_id)
            if not existing_cargo:
                logger.warning("Cargo not found for update: ID %s", cargo_id)
                return None
            updated_data = cargo_data.model_dump(exclude_unset=True)
            updated_cargo = await self._repository.update(cargo_id, updated_data)
            if updated_cargo:
                logger.debug("Cargo updated: %s", updated_cargo)
            return (
                CargoResponse.model_validate(updated_cargo) if updated_cargo else None
            )
        except IntegrityError as e:
            logger.exception("Integrity error while updating cargo")
            raise ValueError(
                "Failed to update cargo due to data integrity error"
            ) from e

    async def delete_cargo(self, cargo_id: int) -> bool:
        """
        Remove uma carga do sistema.
        """
        logger.info("Deleting cargo with ID %s", cargo_id)
        success = await self._repository.delete(cargo_id)
        if success:
            logger.debug("Cargo deleted successfully: ID %s", cargo_id)
        else:
            logger.warning("Failed to delete or cargo not found: ID %s", cargo_id)
        return success

    async def get_cargoes_by_contract(self, contract_id: int) -> List[CargoResponse]:
        """
        Retorna todas as cargas associadas a um contrato.
        """
        logger.info("Fetching cargoes for contract ID %s", contract_id)
        cargoes = await self._repository.find_by_contract_id(contract_id)
        logger.debug("Cargoes found: %d", len(cargoes))
        return [CargoResponse.model_validate(c) for c in cargoes]

    async def get_cargoes_by_status(self, status: CargoStatus) -> List[CargoResponse]:
        """
        Retorna todas as cargas com o status especificado.
        """
        logger.info("Fetching cargoes with status '%s'", status.value)
        cargoes = await self._repository.find_by_status(status)
        logger.debug("Cargoes found: %d", len(cargoes))
        return [CargoResponse.model_validate(c) for c in cargoes]

    async def get_cargoes_by_destination(self, destination: str) -> List[CargoResponse]:
        """
        Retorna todas as cargas com destino correspondente.
        """
        logger.info("Fetching cargoes for destination '%s'", destination)
        cargoes = await self._repository.find_by_destination(destination)
        logger.debug("Cargoes found: %d", len(cargoes))
        return [CargoResponse.model_validate(c) for c in cargoes]
