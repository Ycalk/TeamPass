from typing import Self
from uuid import UUID

from pydantic import BaseModel
from teampass.user.storage import Student as StudentPersistent
from teampass.user.storage import StudentProfile as StudentProfilePersistent
from teampass.user.storage import User as UserPersistent


class Student(BaseModel):
    student_id: str
    first_name: str
    last_name: str
    patronymic: str | None

    @classmethod
    def from_persistent(cls, student: StudentPersistent) -> Self:
        return cls(
            student_id=student.student_id,
            first_name=student.first_name,
            last_name=student.last_name,
            patronymic=student.patronymic,
        )


class User(BaseModel):
    id: UUID
    email: str
    student: Student

    @classmethod
    def from_persistent(cls, user: UserPersistent) -> Self:
        return cls(
            id=user.id,
            email=user.email,
            student=Student.from_persistent(user.student),
        )


class StudentProfile(BaseModel):
    telegram_username: str | None
    vk_profile_link: str | None
    phone_number: str | None
    strengths_text: str | None
    weaknesses_text: str | None
    user: User

    @classmethod
    def from_persistent(cls, student_profile: StudentProfilePersistent) -> Self:
        return cls(
            telegram_username=student_profile.telegram_username,
            vk_profile_link=student_profile.vk_profile_link,
            phone_number=student_profile.phone_number,
            strengths_text=student_profile.strengths_text,
            weaknesses_text=student_profile.weaknesses_text,
            user=User.from_persistent(student_profile.user),
        )
