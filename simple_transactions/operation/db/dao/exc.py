class CommonRepositoryError(Exception):
    """Generic error for repository operations."""


class CommonRepositoryError(CommonRepositoryError):
    """Error not described enough but separate from generic RepositoryError"""

class EntityNotFoundError(CommonRepositoryError):
    """Raised when an entity is not found in the database."""


class ForeignKeyViolation(CommonRepositoryError):
    """Raised when entity modification leads to key violation"""

class UniqueConstraintViolationError(CommonRepositoryError):
    """Raised when a unique constraint is violated."""
