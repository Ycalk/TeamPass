from teampass.domain_core import (
    DomainForbiddenException,
    DomainNotFoundException,
)


class MediaTooLargeException(DomainForbiddenException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class MediaNotFoundException(DomainNotFoundException):
    def __init__(self, message: str) -> None:
        super().__init__(message)
