from pydantic import BaseModel, Field
from teampass.user import User


class UserWithAccessToken(BaseModel):
    access_token: str
    user: User


class AccessTokenResponse(BaseModel):
    access_token: str


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str = Field(description="Тип ошибки")
    message: str = Field(description="Детали ошибки")
