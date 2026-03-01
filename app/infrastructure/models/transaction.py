from sqlalchemy import DATETIME, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Integer
from app.infrastructure.models.base import Base


class Transaction(Base):
    __tablename__ = "Transaction"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=False, index=True)
    created_datetime: Mapped[str] = mapped_column(DATETIME, nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("Account.id"), nullable=False, index=True)

    # orm relationship
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    account: Mapped["Account"] = relationship("Account", back_populates="transactions")

    __table_args__ = (
        Index("ix_transaction_user_id_account_id", "user_id", "account_id"),
    )