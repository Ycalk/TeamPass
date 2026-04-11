from argon2 import PasswordHasher
from dishka import Provider, Scope, provide, provide_all
from dishka.dependency_source import CompositeDependencySource

from .methods import ChangeAdminPasswordMethod, CreateAdminMethod, LoginAdminMethod
from .storage import AdminDAO


class AdminProvider(Provider):
    @provide(scope=Scope.APP)
    def password_hasher(self) -> PasswordHasher:
        return PasswordHasher()

    methods: CompositeDependencySource = provide_all(
        LoginAdminMethod,
        CreateAdminMethod,
        ChangeAdminPasswordMethod,
        scope=Scope.REQUEST,
    )

    data_access_objects: CompositeDependencySource = provide_all(
        AdminDAO,
        scope=Scope.REQUEST,
    )
