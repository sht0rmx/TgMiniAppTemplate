import uuid
from sqlalchemy import UUID, String, BIGINT
from sqlalchemy.orm import Mapped, mapped_column
from modules.db.engine import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(30))
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
