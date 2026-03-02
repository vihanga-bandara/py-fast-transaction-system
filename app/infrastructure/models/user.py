from datetime import datetime, timezone

from sqlalchemy import DATETIME
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Integer, String, DateTime

from app.infrastructure.models.base import Base

class User(Base):
    __tablename__ = "User"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    password_salt: Mapped[str] = mapped_column(String(100), nullable=False)
    created_datetime: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc),
                                                       nullable=False)

    user_permissions: Mapped["list[user_permissions]"] = relationship("UserPermission", back_populates="user")
    transactions: Mapped["list[Transaction]"] = relationship("Transaction", back_populates="user")
