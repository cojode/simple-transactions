from sqlalchemy.orm import DeclarativeBase

from simple_transactions.operation.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
