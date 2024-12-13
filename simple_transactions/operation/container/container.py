"""
Container initialization module.

This module contains functions to initialize container for application.

Initialization of container consists of registration of all application services
and repositories. All registrations are done in singleton scope.

"""
from functools import lru_cache

from punq import Container, Scope

from simple_transactions.operation.db.repositories.transactions import TransactionRepository

from simple_transactions.operation.db.dao.database import Database

from simple_transactions.operation.settings import settings

@lru_cache(1)
def init_container() -> Container:
    """
    Initialize container for application.

    This function uses lru_cache decorator to cache result of container
    initialization. This means that first call to this function will initialize
    container and subsequent calls will return cached result.

    :return: Initialized container.
    :rtype: Container
    """
    return _init_container()

def _init_container() -> Container:
    """
    Initialize container for application.

    This function registers all services and repositories in container.

    :return: Initialized container.
    :rtype: Container
    """
    container = Container()
    container.register(
        Database, scope=Scope.singleton,
        factory=lambda: Database(
            url=str(settings.db_url),
        ))

    container.register(TransactionRepository)

    from simple_transactions.operation.services.transactions import TransactionService
    container.register(
        TransactionService, scope=Scope.singleton
    )

    return container