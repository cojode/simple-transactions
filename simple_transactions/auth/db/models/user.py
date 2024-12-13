from sqlalchemy.orm import Mapped, mapped_column
from simple_transactions.auth.db.base import Base

class UserModel(Base):
    """User model."""
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()