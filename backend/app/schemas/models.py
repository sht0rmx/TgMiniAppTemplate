from pydantic import BaseModel


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    language_code: str
    allows_write_to_pm: bool
    photo_url: str
    

class WebAppLoginRequest(BaseModel):
    initData: str


class RecoveryRequest(BaseModel):
    recovery_code: str


class CreateApiKeyRequest(BaseModel):
    name: str

class SendMessageRequest(BaseModel):
    text: str