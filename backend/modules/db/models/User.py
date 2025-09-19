from sqlalchemy import (
    String,
    BIGINT,
)

from modules.db.engine import Base
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True, nullable=False)
    token_key: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(30))
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)