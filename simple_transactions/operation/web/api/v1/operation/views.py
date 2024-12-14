from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

from punq import Container

from simple_transactions.operation.container.container import init_container

from simple_transactions.operation.services.transactions import (
    TransactionService,
    TransactionPrefetchFailedError,
    TransactionSelfTransactionViolationError,
    TransactionBalanceExhaustedError,
)

http_bearer = HTTPBearer()


class BrowseTransactionsRequest(BaseModel):
    user_from_id: int = Field(...)
    offset: int = Field(...)
    limit: int = Field(...)
    filter_date_after: Optional[date] = Field(default=None)
    filter_date_before: Optional[date] = Field(default=None)
    filter_status: Optional[str] = Field(default=None)


class InitTransactionRequest(BaseModel):
    from_user_username: str = Field(...)
    to_user_username: str = Field(...)
    amount: float = Field(...)


router = APIRouter()


@router.post("/browse")
async def browse_transactions(
    browse_params: BrowseTransactionsRequest,
    container: Container = Depends(init_container),
) -> None:
    transaction_service: TransactionService = container.resolve(TransactionService)
    return await transaction_service.browse_transactions(
        browse_params.user_from_id,
        browse_params.offset,
        browse_params.limit,
        browse_params.filter_date_after,
        browse_params.filter_date_before,
        browse_params.filter_status,
    )


@router.post("/transaction")
async def init_transaction(
    init_params: InitTransactionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    container: Container = Depends(init_container),
) -> None:
    transaction_service: TransactionService = container.resolve(TransactionService)
    try:
        return await transaction_service.process_transaction(
            init_params.from_user_username,
            credentials.credentials,
            init_params.to_user_username,
            init_params.amount,
        )
    except TransactionPrefetchFailedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Transaction prefetch failed"
        )
    except TransactionSelfTransactionViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can not create looped transaction",
        )
    except TransactionBalanceExhaustedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed transaction: insufficient funds",
        )
