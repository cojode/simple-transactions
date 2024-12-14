from simple_transactions.operation.db.dao import CRUDRepository, repository_for

from sqlalchemy import and_

from simple_transactions.operation.db.models.transactions import TransactionModel

import datetime


@repository_for(TransactionModel)
class TransactionRepository(CRUDRepository):
    async def create_transaction(self, **transaction_fields) -> TransactionModel:
        return await self.atomic.create(self, **transaction_fields)

    async def update_transaction_status(self, transaction_id: int, new_status: str):
        return await self.atomic.update(
            self, fields={"status": new_status}, id=transaction_id
        )

    async def browse_transactions_by_user_from_id(
        self,
        user_from_id: int,
        offset: int,
        limit: int,
        filter_date_after: datetime.date | None = None,
        filter_date_before: datetime.date | None = None,
        filter_status: str | None = None,
    ) -> list[TransactionModel]:
        filters = [
            self.model.from_user_id == user_from_id,
        ]
        if filter_date_after:
            filters.append(self.model.date >= filter_date_after)
        if filter_date_before:
            filters.append(self.model.date <= filter_date_before)
        if filter_status:
            filters.append(self.model.status == filter_status)
        atomic_read = await self.atomic.read(
            self, limit=limit, offset=offset, where=and_(*filters)
        )
        return atomic_read if atomic_read else []

    async def save_transaction(self, transaction: TransactionModel):
        await self.atomic.save(self, transaction)

    async def modify_transaction_users_balances(
        self, transaction: TransactionModel, amount: int
    ):
        async def atomic_operation(session):
            transaction_with_relations = await self.load_related(
                transaction, ["from_user", "to_user"], session
            )
            transaction_with_relations.from_user.balance -= amount
            transaction_with_relations.to_user.balance += amount
            await self.save(transaction_with_relations.from_user, session)
            await self.save(transaction_with_relations.from_user, session)

        return await self.run_atomic(atomic_operation)
