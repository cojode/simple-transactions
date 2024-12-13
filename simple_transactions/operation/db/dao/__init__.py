"""Routes for swagger and redoc."""

from .crud import CRUDRepository
from .extended import ExtendedCRUDRepository

from .interface import repository_for

__all__ = ["repository_for"]
