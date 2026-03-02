from sqlalchemy import BigInteger, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Integer, String
from app.infrastructure.models.base import Base

class Account(Base):
    __tablename__ = "Account"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    balance: Mapped[int] = mapped_column(BigInteger, server_default=text("0"), nullable=False)

    transactions: Mapped["list[Transaction]"] = relationship("Transaction", back_populates="account")