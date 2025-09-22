import uuid
import secrets
from datetime import datetime

from sqlalchemy import (
    UUID, String, Boolean, DateTime, ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from modules.db.engine import Base
from modules.db.models.User import User



class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[str] = mapped_column(String(64), nullable=False)
    ip_address: Mapped[str] = mapped_column(String, nullable=False)
    token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, default=lambda: secrets.token_urlsafe(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", backref="refresh_tokens")