import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, func

from app.domain.models.base import BaseModel

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self._session = session
        self._model_class = model_class

    async def create(self, data: Dict[str, Any]) -> T:
        """
        Creates a new instance of the model with the provided data.
        """
        logger.info("Creating new %s record", self._model_class.__name__)
        try:
            entity = self._model_class(**data)
            self._session.add(entity)
            await self._session.commit()
            await self._session.refresh(entity)
            logger.debug("Created entity: %s", entity)
            return entity
        except SQLAlchemyError as e:
            logger.exception("Failed to create %s", self._model_class.__name__)
            await self._session.rollback()
            raise e

    async def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Retrieve an entity by its primary key.
        """
        logger.info("Fetching %s with ID: %s", self._model_class.__name__, entity_id)
        return await self._session.get(self._model_class, entity_id)

    async def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        Return all records that match the optional filters.
        """
        logger.info("Fetching all %s records", self._model_class.__name__)
        query = select(self._model_class)
        query = self._apply_filters(query, filters)
        result = await self._session.execute(query)
        items = result.scalars().all()
        logger.debug("Found %d records", len(items))
        return items

    async def update(self, entity_id: int, data: Dict[str, Any]) -> Optional[T]:
        """
        Update an existing record with new data.
        """
        logger.info("Updating %s ID: %s", self._model_class.__name__, entity_id)
        try:
            entity = await self.get_by_id(entity_id)
            if entity:
                for key, value in data.items():
                    setattr(entity, key, value)
                await self._session.commit()
                await self._session.refresh(entity)
                logger.debug("Updated entity: %s", entity)
            else:
                logger.warning(
                    "%s not found for update: ID %s",
                    self._model_class.__name__,
                    entity_id,
                )
            return entity
        except SQLAlchemyError as e:
            logger.exception("Failed to update %s", self._model_class.__name__)
            await self._session.rollback()
            raise e

    async def delete(self, entity_id: int) -> bool:
        """
        Delete an entity by ID.
        """
        logger.info("Deleting %s with ID: %s", self._model_class.__name__, entity_id)
        try:
            entity = await self.get_by_id(entity_id)
            if entity:
                await self._session.delete(entity)
                await self._session.commit()
                logger.debug("Deleted entity: ID %s", entity_id)
                return True
            logger.warning(
                "%s not found for deletion: ID %s",
                self._model_class.__name__,
                entity_id,
            )
            return False
        except SQLAlchemyError as e:
            logger.exception("Failed to delete %s", self._model_class.__name__)
            await self._session.rollback()
            raise e

    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[T], int]:
        """
        Paginate through records, optionally filtered.
        """
        logger.info(
            "Paginating %s: page=%d, page_size=%d",
            self._model_class.__name__,
            page,
            page_size,
        )

        if page_size == 0:
            return [], await self.count(filters)

        # Ensure valid pagination values
        page = max(page, 1)
        page_size = max(page_size, 1)
        offset = (page - 1) * page_size

        query = select(self._model_class)
        query = self._apply_filters(query, filters)
        query = query.offset(offset).limit(page_size)

        result = await self._session.execute(query)
        items = result.scalars().all()
        total = await self.count(filters)

        logger.debug("Paginated result: %d items out of %d total", len(items), total)
        return items, total

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records matching filters.
        """
        logger.info("Counting %s records", self._model_class.__name__)
        query = select(func.count()).select_from(self._model_class)
        query = self._apply_filters(query, filters)
        result = await self._session.execute(query)
        total = result.scalar_one()
        logger.debug("Count result: %d", total)
        return total

    def _apply_filters(self, query, filters: Optional[Dict[str, Any]]):
        """
        Apply filtering conditions to a SQLAlchemy query dynamically.
        """
        if filters:
            for attr, value in filters.items():
                if hasattr(self._model_class, attr):
                    query = query.where(getattr(self._model_class, attr) == value)
        return query
