from argon2 import PasswordHasher
from dishka import Provider, Scope, provide, provide_all
from dishka.dependency_source import CompositeDependencySource

from .methods import (
    ChangeUserEmailMethod,
    ChangeUserPasswordMethod,
    LoginUserMethod,
    RegisterUserMethod,
    UpdateStudentProfileMethod,
)
from .storage import StudentDAO, StudentProfileDAO, UserDAO


class UserProvider(Provider):
    @provide(scope=Scope.APP)
    def password_hasher(self) -> PasswordHasher:
        return PasswordHasher()

    methods: CompositeDependencySource = provide_all(
        LoginUserMethod,
        RegisterUserMethod,
        ChangeUserEmailMethod,
        ChangeUserPasswordMethod,
        UpdateStudentProfileMethod,
        scope=Scope.REQUEST,
    )

    data_access_objects: CompositeDependencySource = provide_all(
        StudentDAO,
        StudentProfileDAO,
        UserDAO,
        scope=Scope.REQUEST,
    )
