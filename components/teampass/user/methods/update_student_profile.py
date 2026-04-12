from typing import Annotated, Final, override
from uuid import UUID

import structlog
from opentelemetry import trace
from pydantic import BaseModel, StringConstraints
from teampass.domain_core import DomainMethod
from teampass.user.dto import StudentProfile
from teampass.user.storage import UserDAO

from .exceptions import UserNotFoundException

_tracer: Final[trace.Tracer] = trace.get_tracer(__name__)
_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)


class UpdateStudentProfilePayload(BaseModel):
    telegram_username: Annotated[
        str | None, StringConstraints(pattern=r"^([A-Za-z0-9_]{5,32})?$")
    ] = None
    vk_profile_link: Annotated[
        str | None,
        StringConstraints(pattern=r"^(https?://(www\.)?vk\.com/[a-zA-Z0-9_.]{5,32})?$"),
    ] = None
    phone_number: Annotated[
        str | None, StringConstraints(pattern=r"^(\+?\d{10,15})?$")
    ] = None
    strengths_text: str | None = None
    weaknesses_text: str | None = None


class UpdateStudentProfileCommand(UpdateStudentProfilePayload):
    user_id: UUID


class UpdateStudentProfileMethod(
    DomainMethod[UpdateStudentProfileCommand, StudentProfile]
):
    def __init__(self, user_dao: UserDAO) -> None:
        self.user_dao: UserDAO = user_dao

    @override
    async def __call__(self, command: UpdateStudentProfileCommand) -> StudentProfile:
        with _tracer.start_as_current_span("user.update_student_profile") as span:
            span.set_attribute("user.id", str(command.user_id))
            logger = _logger.bind(user_id=str(command.user_id))

            logger.info("updating_student_profile")

            user = await self.user_dao.find_by_id_with_loaded_student_profile(
                command.user_id
            )
            if user is None:
                logger.error("user_not_found")
                raise UserNotFoundException(command.user_id)

            profile = user.student_profile

            if command.telegram_username is not None:
                profile.telegram_username = (
                    None
                    if command.telegram_username == ""
                    else command.telegram_username
                )
            if command.vk_profile_link is not None:
                profile.vk_profile_link = (
                    None if command.vk_profile_link == "" else command.vk_profile_link
                )
            if command.phone_number is not None:
                profile.phone_number = (
                    None if command.phone_number == "" else command.phone_number
                )
            if command.strengths_text is not None:
                profile.strengths_text = (
                    None if command.strengths_text == "" else command.strengths_text
                )
            if command.weaknesses_text is not None:
                profile.weaknesses_text = (
                    None if command.weaknesses_text == "" else command.weaknesses_text
                )

            await self.user_dao.save(user)
            await self.user_dao.commit()
            await user.awaitable_attrs.student

            logger.info("student_profile_updated")

            return StudentProfile.from_persistent(profile)
