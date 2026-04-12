from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID

import jwt
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from teampass.entrypoint.settings import EntrypointSettings

from .exceptions import CustomHTTPException


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class _TokenPayload(BaseModel):
    sub: UUID
    exp: int
    iat: int
    type: TokenType


def create_token(
    user_id: UUID, token_type: TokenType, settings: EntrypointSettings
) -> str:
    now = datetime.now()
    if token_type == TokenType.ACCESS:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    elif token_type == TokenType.REFRESH:
        expires_delta = timedelta(days=settings.refresh_token_expire_days)

    payload = _TokenPayload(
        sub=user_id,
        exp=int((now + expires_delta).timestamp()),
        iat=int(now.timestamp()),
        type=token_type,
    )

    return jwt.encode(
        payload.model_dump(mode="json"),
        settings.secret_key,
        algorithm=settings.jwt_encoding_algorithm,
    )


def verify_token(
    token: str, token_type: TokenType, settings: EntrypointSettings
) -> UUID:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_encoding_algorithm]
        )

        token_data = _TokenPayload(**payload)

        if token_data.type != token_type:
            raise CustomHTTPException(
                error="InvalidTokenError",
                message=f"Invalid token type: expected {token_type}, "
                + f"got {token_data.type}",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if token_data.exp < int(datetime.now().timestamp()):
            raise CustomHTTPException(
                error="TokenExpiredError",
                message="Token expired",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        return token_data.sub

    except jwt.InvalidTokenError as e:
        raise CustomHTTPException(
            error="InvalidTokenError",
            message=f"Invalid token: {str(e)}",
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from e


security = HTTPBearer(
    scheme_name="Основная авторизация",
    description=(
        "Для использования API необходимо передать токен в заголовке "
        "Authorization в формате 'Bearer <токен>'."
    ),
)


@inject
def get_current_user_id(
    settings: FromDishka[EntrypointSettings],
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    return verify_token(credentials.credentials, TokenType.ACCESS, settings)


def set_refresh_token_cookie(
    response: Response, refresh_token: str, settings: EntrypointSettings
) -> None:
    response.set_cookie(
        key=settings.refresh_token_cookie_name,
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 86400,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/",
    )


def clear_refresh_token_cookie(
    response: Response, settings: EntrypointSettings
) -> None:
    response.delete_cookie(key=settings.refresh_token_cookie_name, path="/")
