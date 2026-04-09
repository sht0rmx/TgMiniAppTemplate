from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    language_code: str
    allows_write_to_pm: bool
    photo_url: str


class LinkedAccounts(BaseModel):
    telegram: bool = False
    yandex: bool = False


class UserResponse(BaseModel):
    id: str
    telegram_id: int
    username: Optional[str] = None
    name: str
    role: str
    avatar_url: Optional[str] = None
    last_seen: str
    created_at: str
    linked_accounts: LinkedAccounts = LinkedAccounts()


class WebAppLoginRequest(BaseModel):
    initData: str


class YandexLoginRequest(BaseModel):
    code: str


class LinkYandexRequest(BaseModel):
    code: str


class RecoveryRequest(BaseModel):
    recovery_code: str


class CreateApiKeyRequest(BaseModel):
    name: str

class SendMessageRequest(BaseModel):
    text: str