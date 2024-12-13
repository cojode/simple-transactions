from simple_transactions.operation.db.dao import ExtendedCRUDRepository, repository_for

from simple_transactions.operation.db.models.transactions import TransactionModel

import datetime

@repository_for(TransactionModel)
class TransactionRepository(ExtendedCRUDRepository[TransactionModel]):
    async def create_transaction(self, **transaction_fields) -> TransactionModel:
        return await self.create(**transaction_fields)

    async def get_transaction_by_id(self, transaction_id: int) -> TransactionModel | None:
        return await self.find_by_id(item_id=transaction_id)
    
    async def browse_transactions_by_user_from_id(
        self, user_from_id: int, offset: int, limit: int, date_from: datetime.date, date_to: datetime.date, specified_status: 
    ) -> list[TransactionModel]:
        ...
