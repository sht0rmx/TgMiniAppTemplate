from pydantic import BaseModel


class UserDto(BaseModel):
    initData: str
