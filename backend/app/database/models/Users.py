import uuid

from sqlalchemy import BigInteger, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, unique=True)
    name = Column(String(150))
    role = Column(String, default="user")
    avatar_url = Column(String(200))
    last_seen = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
