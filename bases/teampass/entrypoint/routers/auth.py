from typing import Final

import structlog
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request, Response, status
from opentelemetry import trace
from teampass.entrypoint.exceptions import CustomHTTPException
from teampass.entrypoint.scheme import (
    AccessTokenResponse,
    ErrorResponse,
    MessageResponse,
    UserWithAccessToken,
)
from teampass.entrypoint.security import (
    TokenType,
    clear_refresh_token_cookie,
    create_token,
    set_refresh_token_cookie,
    verify_token,
)
from teampass.entrypoint.settings import EntrypointSettings
from teampass.user import (
    LoginUserCommand,
    LoginUserMethod,
    RegisterUserCommand,
    RegisterUserMethod,
)

_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    route_class=DishkaRoute,
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Не корректное соответствие student_id и ФИО",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Студент с таким student_id не найден",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "Студент с таким student_id или email уже существует",
        },
    },
)
async def register_user(
    command: RegisterUserCommand,
    register_user_method: FromDishka[RegisterUserMethod],
    settings: FromDishka[EntrypointSettings],
    response: Response,
) -> UserWithAccessToken:
    span = trace.get_current_span()
    span.set_attribute("user.email", command.email)
    span.set_attribute("user.student_id", command.student_id)
    logger = _logger.bind(email=command.email, student_id=command.student_id)

    logger.info("processing_register_user_request")

    user = await register_user_method(command)

    span.set_attribute("user.id", str(user.id))
    logger.info("generating_tokens")

    access_token = create_token(user.id, TokenType.ACCESS, settings)
    refresh_token = create_token(user.id, TokenType.REFRESH, settings)
    set_refresh_token_cookie(response, refresh_token, settings)

    logger.info("register_user_request_processed")
    return UserWithAccessToken(access_token=access_token, user=user)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Не корректный логин или пароль",
        },
    },
)
async def login_user(
    command: LoginUserCommand,
    login_user_method: FromDishka[LoginUserMethod],
    settings: FromDishka[EntrypointSettings],
    response: Response,
) -> UserWithAccessToken:
    span = trace.get_current_span()
    span.set_attribute("user.email", command.email)
    logger = _logger.bind(email=command.email)

    logger.info("processing_login_user_request")

    user = await login_user_method(command)

    span.set_attribute("user.id", str(user.id))
    logger.info("generating_tokens")

    access_token = create_token(user.id, TokenType.ACCESS, settings)
    refresh_token = create_token(user.id, TokenType.REFRESH, settings)
    set_refresh_token_cookie(response, refresh_token, settings)

    logger.info("login_user_request_processed")
    return UserWithAccessToken(access_token=access_token, user=user)


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Refresh токена нет в куках / невалиден / истек",
        },
    },
)
async def refresh_token(
    request: Request,
    settings: FromDishka[EntrypointSettings],
) -> AccessTokenResponse:
    span = trace.get_current_span()
    logger = _logger.bind()
    logger.info("processing_refresh_token_request")

    refresh_token = request.cookies.get(settings.refresh_token_cookie_name)
    if refresh_token is None:
        logger.error("refresh_token_not_found_in_cookies")
        raise CustomHTTPException(
            error="NoRefreshToken",
            message="Refresh token not found in cookies",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user_id = verify_token(refresh_token, TokenType.REFRESH, settings)
    span.set_attribute("user.id", str(user_id))
    logger = logger.bind(user_id=str(user_id))

    logger.info("generating_new_access_token")
    access_token = create_token(user_id, TokenType.ACCESS, settings)

    logger.info("refresh_token_request_processed")
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout")
async def logout(
    response: Response, settings: FromDishka[EntrypointSettings]
) -> MessageResponse:
    _logger.info("processing_logout_request")
    clear_refresh_token_cookie(response, settings)
    _logger.info("logout_request_processed")
    return MessageResponse(message="Logged out successfully")
