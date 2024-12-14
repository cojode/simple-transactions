from dataclasses import dataclass
from typing import Type, TypeVar, List, Optional, Any, Dict, Callable, Coroutine
from sqlalchemy import select as sql_select, update as sql_update, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload, joinedload

from .database import Database
from .exc import CommonRepositoryError

T = TypeVar("T")


@dataclass
class CRUDRepository:
    database: Database
    model: Type[T]

    async def create(
        self, entity: Optional[T] = None, session: AsyncSession = None, **kwargs: Any
    ) -> T:
        instance = entity if entity else self.model(**kwargs)
        session.add(instance)
        await session.flush([instance])
        return instance

    async def read(
        self,
        session: AsyncSession,
        where: Optional[Any] = None,
        order_by: Optional[Any] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        only_first: bool = False,
    ) -> List[T] | Optional[T]:
        query = sql_select(self.model)

        if where is not None:
            query = query.filter(where)
        if order_by is not None:
            query = query.order_by(order_by)
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        result = await session.execute(query)
        if only_first is not None:
            return result.scalars().first()
        return result.scalars().all()

    async def update(
        self, session: AsyncSession = None, fields: Dict[str, Any] = {}, **filters: Any
    ) -> int:
        if not fields:
            raise ValueError("No fields provided to update")
        query = sql_update(self.model).values(**fields).filter_by(**filters)
        result = await session.execute(query)
        return result.rowcount

    async def delete(self, session: AsyncSession = None, **filters: Any) -> int:
        query = sql_delete(self.model).filter_by(**filters)
        result = await session.execute(query)
        return result.rowcount

    async def save(self, entity: T, session: AsyncSession = None) -> T:
        session.add(entity)
        await session.flush()
        await session.refresh(entity)
        return entity

    async def run_atomic(
        self, operation: Callable[[AsyncSession], Coroutine[Any, Any, Any]]
    ) -> Any:
        async with self.database.get_transactional_session() as session:
            result = await operation(session)
            await session.commit()
            return result

    async def load_related(
        self, entity: T, relationships: List[str], session: AsyncSession
    ) -> T | None:
        query = (
            sql_select(self.model)
            .options(*[selectinload(getattr(self.model, rel)) for rel in relationships])
            .filter_by(id=entity.id)
        )
        result = await session.execute(query)
        return result.scalars().first()

    @dataclass
    class atomic:
        @staticmethod
        async def create(
            repo: "CRUDRepository", entity: Optional[T] = None, **kwargs: Any
        ) -> T:
            async with repo.database.get_session() as session:
                return await repo.create(entity=entity, session=session, **kwargs)

        @staticmethod
        async def read(
            repo: "CRUDRepository",
            where: Optional[Any] = None,
            order_by: Optional[Any] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            only_first: bool = False,
            **filters: Any
        ) -> List[T]:
            async with repo.database.get_session() as session:
                return await repo.read(
                    session=session,
                    only_first=only_first,
                    where=where,
                    order_by=order_by,
                    limit=limit,
                    offset=offset,
                    **filters
                )

        @staticmethod
        async def update(
            repo: "CRUDRepository", fields: Dict[str, Any], **filters: Any
        ) -> int:
            async with repo.database.get_session() as session:
                return await repo.update(session=session, fields=fields, **filters)

        @staticmethod
        async def delete(repo: "CRUDRepository", **filters: Any) -> int:
            async with repo.database.get_session() as session:
                return await repo.delete(session=session, **filters)

        @staticmethod
        async def save(repo: "CRUDRepository", entity: T) -> T:
            async with repo.database.get_session() as session:
                return await repo.save(entity=entity, session=session)
