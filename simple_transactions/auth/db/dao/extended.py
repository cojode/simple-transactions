from typing import List, Optional, Any, Dict, TypeVar
from sqlalchemy import asc, desc
from . import CRUDRepository

T = TypeVar("T")


class ExtendedCRUDRepository(CRUDRepository[T]):
    async def find_all(self, **filters) -> List[T]:
        """
        Retrieve all entities matching specified filters.
        """
        return await self.read(only_first=False, **filters)

    async def find_by_id(self, item_id: int) -> Optional[T]:
        """
        Retrieve an entity by its ID.
        """
        return await self.find_one(id=item_id)

    async def count_all(self) -> int:
        """
        Count all entities in the model.
        """
        entities = await self.find_all()
        return len(entities)

    async def count_by_filter(self, **filters) -> int:
        """
        Count entities matching specific filters.
        """
        entities = await self.find_all(**filters)
        return len(entities)

    async def find_and_count(self, **filters) -> dict:
        values = await self.find_all(**filters)
        return {"values": values, "count": len(values)}

    async def find_with_pagination(
        self, page: int = 1, per_page: int = 10, **filters
    ) -> List[T]:
        """
        Paginate results with filters.
        """
        offset = (page - 1) * per_page
        return await self.read(limit=per_page, offset=offset, **filters)

    async def find_with_ordering(
        self, order_by: str, descending: bool = False, **filters
    ) -> List[T]:
        """
        Order results by a column.
        """
        order = (
            desc(getattr(self.model, order_by))
            if descending
            else asc(getattr(self.model, order_by))
        )
        print("chlen", order)
        return await self.read(order_by=order, **filters)

    async def exists(self, **filters) -> bool:
        """
        Check if any entity exists that matches the filters.
        """
        entity = await self.find_one(**filters)
        return entity is not None

    async def find_or_create(
        self, defaults: Optional[Dict[str, Any]] = None, **filters
    ) -> T:
        """
        Find or create an entity.
        """
        entity = await self.find_one(**filters)
        return entity if entity else await self.create(**{**defaults, **filters})

    async def find_one(self, **filters) -> Optional[T]:
        """
        Retrieve a single entity matching the filters.
        """
        return await self.read(only_first=True, **filters)

    async def update_by_filter(self, fields: Dict[str, Any], **filters) -> int:
        """
        Update entities based on filters.
        """
        return await self.update(fields=fields, **filters)

    async def delete_by_filter(self, **filters) -> int:
        """
        Delete entities matching the filters.
        """
        return await self.delete(**filters)
