from argon2 import PasswordHasher
from dishka import Provider, Scope, provide, provide_all
from dishka.dependency_source import CompositeDependencySource
from teampass.user.storage import StudentDAO, StudentProfileDAO, UserDAO

from .methods import LoginUserMethod, RegisterUserMethod


class UserProvider(Provider):
    @provide(scope=Scope.APP)
    def password_hasher(self) -> PasswordHasher:
        return PasswordHasher()

    methods: CompositeDependencySource = provide_all(
        LoginUserMethod,
        RegisterUserMethod,
        scope=Scope.REQUEST,
    )

    data_access_objects: CompositeDependencySource = provide_all(
        StudentDAO,
        StudentProfileDAO,
        UserDAO,
        scope=Scope.REQUEST,
    )
