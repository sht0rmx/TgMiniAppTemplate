from sqlalchemy import (
    Column,
    String,
)

from modules.db.engine import Base


class Locales(Base):
    __tablename__ = "locales"
    id = Column(String, primary_key=True, autoincrement=True)
    locale_alias = Column(String(10), unique=True)
    locale_description = Column(String)
    frontend_translation_pth = Column(String)
    bot_translation_pth = Column
