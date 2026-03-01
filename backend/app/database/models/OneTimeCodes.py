import uuid

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.models import Base


class OneTimeCode(Base):
    __tablename__ = "one_time_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login_id = Column(String, unique=True, nullable=False)
    code_hash = Column(String, nullable=False)
    sse_login_id = Column(String, nullable=True)
    fingerprint = Column(String, nullable=False)
    ip = Column(String, nullable=False)
    accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now(),)
