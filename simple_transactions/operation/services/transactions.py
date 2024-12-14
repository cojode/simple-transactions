from simple_transactions.operation.db.repositories.transactions import (
    TransactionRepository,
)
from simple_transactions.operation.services.auth_client import (
    AuthClientService,
    AuthClientServiceError,
)

from simple_transactions.operation.services.utils import model_row_to_dict

from loguru import logger

from enum import Enum

import datetime


class TransactionServiceError(Exception): ...


class TransactionPrefetchFailedError(TransactionServiceError): ...


class TransactionSelfTransactionViolationError(TransactionServiceError): ...


class TransactionBalanceExhaustedError(TransactionServiceError): ...


class TransactionBalanceUpdateFailed(TransactionServiceError): ...


class TransactionStatus(str, Enum):
    pending: str = "PENDING"
    success: str = "SUCCESS"
    failure: str = "FAILURE"


class TransactionService:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        auth_client_service: AuthClientService,
    ):
        self.transaction_repository: TransactionRepository = transaction_repository
        self.auth_client_service: AuthClientService = auth_client_service

    async def browse_transactions(
        self,
        user_from_id: int,
        offset: int,
        limit: int,
        filter_date_after: datetime.date | None = None,
        filter_date_before: datetime.date | None = None,
        filter_status: str | None = None,
    ):
        return await self.transaction_repository.browse_transactions_by_user_from_id(
            user_from_id,
            offset,
            limit,
            filter_date_after,
            filter_date_before,
            filter_status,
        )

    async def process_transaction(
        self,
        from_user_username: str,
        from_user_token: str,
        to_user_username: str,
        amount: int,
    ):
        if from_user_username == to_user_username:
            logger.info(f"User {from_user_username} attempted to transact same user.")
            raise TransactionSelfTransactionViolationError

        try:
            user_from, user_to = await self.auth_client_service.prefetch_transaction(
                from_user_username=from_user_username,
                from_user_token=from_user_token,
                to_user_username=to_user_username,
            )
            logger.info(
                f"Transaction prefetch successfull: fetched user_from: {user_from}, user_to: {user_to}"
            )
        except AuthClientServiceError:
            raise TransactionPrefetchFailedError

        sufficient_balance = user_from.get("balance") >= amount

        new_transaction = await self.transaction_repository.create_transaction(
            from_user_id=user_from.get("id", None),
            to_user_id=user_to.get("id", None),
            status=(
                TransactionStatus.pending
                if sufficient_balance
                else TransactionStatus.failure
            ),
            amount=amount,
            date=datetime.date.today(),
        )

        logger.info(
            f"New transaction successfully registered: {model_row_to_dict(new_transaction)}"
        )

        if not sufficient_balance:
            logger.info(
                f"Transaction marked as failed - unsufficient funds for user {from_user_username}: "
            )
            raise TransactionBalanceExhaustedError

        try:
            await self.transaction_repository.modify_transaction_users_balances(
                new_transaction, amount
            )
            new_transaction.status = TransactionStatus.success
            await self.transaction_repository.save_transaction(new_transaction)
        except:
            new_transaction.status = TransactionStatus.failure
            await self.transaction_repository.save_transaction(new_transaction)
            raise TransactionBalanceUpdateFailed
