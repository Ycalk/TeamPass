from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request, Response, status
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
    user = await register_user_method(command)
    access_token = create_token(user.id, TokenType.ACCESS, settings)
    refresh_token = create_token(user.id, TokenType.REFRESH, settings)
    set_refresh_token_cookie(response, refresh_token, settings)
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
    user = await login_user_method(command)
    access_token = create_token(user.id, TokenType.ACCESS, settings)
    refresh_token = create_token(user.id, TokenType.REFRESH, settings)
    set_refresh_token_cookie(response, refresh_token, settings)
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
    refresh_token = request.cookies.get(settings.refresh_token_cookie_name)
    if refresh_token is None:
        raise CustomHTTPException(
            error="NoRefreshToken",
            message="Refresh token not found in cookies",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user_id = verify_token(refresh_token, TokenType.REFRESH, settings)
    access_token = create_token(user_id, TokenType.ACCESS, settings)
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout")
async def logout(
    response: Response, settings: FromDishka[EntrypointSettings]
) -> MessageResponse:
    clear_refresh_token_cookie(response, settings)
    return MessageResponse(message="Logged out successfully")
