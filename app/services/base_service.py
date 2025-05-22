import logging
from typing import Generic, TypeVar, List, Optional, Tuple, Any

ModelType = TypeVar("ModelType")

logger = logging.getLogger(__name__)


class BaseService(Generic[ModelType]):
    def __init__(self, repository, response_schema=None):
        self._repository = repository
        self._response_schema = response_schema

    async def get_paginated(
        self, page: int = 1, page_size: int = 10, filters: Optional[dict] = None
    ) -> Tuple[List[Any], int]:
        logger.debug(
            f"Fetching paginated data: page={page}, page_size={page_size}, filters={filters or {}}"
        )

        try:
            items, total = await self._repository.get_paginated(
                page, page_size, filters
            )
            logger.info(f"Retrieved {len(items)} items (total: {total})")
        except Exception as e:
            logger.exception("Failed to fetch paginated data" + e)
            raise

        if self._response_schema and items:
            items = [self._response_schema.model_validate(i) for i in items]

        return items, total
