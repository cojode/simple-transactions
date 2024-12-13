from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from simple_transactions.operation.db.base import Base
import datetime

class TransactionModel(Base):
    """Transaction model."""
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id'))
    to_user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id'))
    status: Mapped[str] = mapped_column()
    amount: Mapped[int] = mapped_column()
    date: Mapped[datetime.date] = mapped_column()
    
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])