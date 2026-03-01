from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.infrastructure.models.base import Base


class UserPermission(Base):
    __tablename__ = "UserPermission"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=False)
    user_role_id: Mapped[int] = mapped_column(ForeignKey("UserRole.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_permissions")
