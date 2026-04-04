from typing import Protocol


class DomainMethod[TCommand, TResult](Protocol):
    async def __call__(self, command: TCommand) -> TResult: ...


class DomainException(Exception):
    def __init__(self, message: str) -> None:
        self.message: str = message
        super().__init__(message)


class DomainUnauthorizedException(DomainException):
    pass


class DomainForbiddenException(DomainException):
    pass


class DomainNotFoundException(DomainException):
    pass


class DomainConflictException(DomainException):
    pass
