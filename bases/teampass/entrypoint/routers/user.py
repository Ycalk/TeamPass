from typing import Final
from uuid import UUID

import structlog
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status
from opentelemetry import trace
from teampass.entrypoint.exceptions import CustomHTTPException
from teampass.entrypoint.scheme import ErrorResponse
from teampass.entrypoint.security import get_current_user_id
from teampass.user import (
    ChangeUserEmailCommand,
    ChangeUserEmailMethod,
    ChangeUserEmailPayload,
    ChangeUserPasswordCommand,
    ChangeUserPasswordMethod,
    ChangeUserPasswordPayload,
    StudentProfile,
    UpdateStudentProfileCommand,
    UpdateStudentProfileMethod,
    UpdateStudentProfilePayload,
    User,
)
from teampass.user.storage import UserDAO

_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Не валидный access токен",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Пользователь не найден",
        },
    },
    route_class=DishkaRoute,
)


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(
    user_dao: FromDishka[UserDAO],
    user_id: UUID = Depends(get_current_user_id),
) -> User:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_get_me_request")

    user = await user_dao.find_by_id_with_loaded_student(user_id)
    if user is None:
        logger.error("user_not_found")
        raise CustomHTTPException(
            error="UserNotFound",
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    logger.info("get_me_request_processed")
    return User.from_persistent(user)


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(
    user_dao: FromDishka[UserDAO],
    user_id: UUID,
    _: UUID = Depends(get_current_user_id),
) -> User:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_get_user_request")

    user = await user_dao.find_by_id_with_loaded_student(user_id)
    if user is None:
        logger.error("user_not_found")
        raise CustomHTTPException(
            error="UserNotFound",
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    logger.info("get_user_request_processed")
    return User.from_persistent(user)


@router.patch(
    "/me/email",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "Пользователь с такой почтой уже существует",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Не корректный пароль",
        },
    },
)
async def change_email(
    payload: ChangeUserEmailPayload,
    method: FromDishka[ChangeUserEmailMethod],
    user_id: UUID = Depends(get_current_user_id),
) -> User:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_change_email_request")

    res = await method(ChangeUserEmailCommand(user_id=user_id, **payload.model_dump()))
    logger.info("change_email_request_processed")
    return res


@router.patch(
    "/me/password",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Не корректный пароль",
        },
    },
)
async def change_password(
    payload: ChangeUserPasswordPayload,
    method: FromDishka[ChangeUserPasswordMethod],
    user_id: UUID = Depends(get_current_user_id),
) -> User:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_change_password_request")

    res = await method(
        ChangeUserPasswordCommand(user_id=user_id, **payload.model_dump())
    )
    logger.info("change_password_request_processed")
    return res


@router.patch("/me/profile", status_code=status.HTTP_200_OK)
async def update_profile(
    payload: UpdateStudentProfilePayload,
    method: FromDishka[UpdateStudentProfileMethod],
    user_id: UUID = Depends(get_current_user_id),
) -> StudentProfile:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_update_profile_request")

    res = await method(
        UpdateStudentProfileCommand(user_id=user_id, **payload.model_dump())
    )
    logger.info("update_profile_request_processed")
    return res


@router.get("/me/profile", status_code=status.HTTP_200_OK)
async def get_my_profile(
    student_dao: FromDishka[UserDAO],
    user_id: UUID = Depends(get_current_user_id),
) -> StudentProfile:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_get_my_profile_request")

    user = await student_dao.find_by_id_with_loaded_student_profile(user_id)
    if user is None:
        logger.error("user_not_found")
        raise CustomHTTPException(
            error="UserNotFound",
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    logger.info("get_my_profile_request_processed")
    return StudentProfile.from_persistent(user.student_profile)


@router.get("/{user_id}/profile", status_code=status.HTTP_200_OK)
async def get_user_profile(
    student_dao: FromDishka[UserDAO],
    user_id: UUID,
    _: UUID = Depends(get_current_user_id),
) -> StudentProfile:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_get_user_profile_request")

    user = await student_dao.find_by_id_with_loaded_student_profile(user_id)
    if user is None:
        logger.error("user_not_found")
        raise CustomHTTPException(
            error="UserNotFound",
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    logger.info("get_user_profile_request_processed")
    return StudentProfile.from_persistent(user.student_profile)
