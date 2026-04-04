from argon2 import PasswordHasher
from dishka import Provider, Scope, provide, provide_all
from dishka.dependency_source import CompositeDependencySource

from .methods import LoginMethod, RegisterUserMethod


class UserProvider(Provider):
    @provide(scope=Scope.APP)
    def password_hasher(self) -> PasswordHasher:
        return PasswordHasher()

    methods: CompositeDependencySource = provide_all(
        LoginMethod,
        RegisterUserMethod,
        scope=Scope.REQUEST,
    )
