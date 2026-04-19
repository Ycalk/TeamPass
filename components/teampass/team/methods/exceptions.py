from uuid import UUID

from teampass.domain_core import (
    DomainConflictException,
    DomainForbiddenException,
    DomainNotFoundException,
)


class InvitationNotFoundException(DomainNotFoundException):
    def __init__(self, invitation_id: UUID) -> None:
        self.invitation_id: UUID = invitation_id
        super().__init__(f"Invitation with ID {invitation_id} not found")


class InvitationDeleteForbiddenException(DomainForbiddenException):
    def __init__(self, user_id: UUID, invitation_id: UUID) -> None:
        self.user_id: UUID = user_id
        self.invitation_id: UUID = invitation_id
        super().__init__(
            f"User {user_id} is not allowed to delete invitation {invitation_id}"
        )


class UserAlreadyInTeamException(DomainConflictException):
    def __init__(self, user_id: UUID) -> None:
        self.user_id: UUID = user_id
        super().__init__(f"User with ID {user_id} is already in a team")


class UserNotInTeamException(DomainForbiddenException):
    def __init__(self, user_id: UUID) -> None:
        self.user_id: UUID = user_id
        super().__init__(f"User with ID {user_id} is not in a team")


class UserNotCaptainException(DomainForbiddenException):
    def __init__(self, user_id: UUID) -> None:
        self.user_id: UUID = user_id
        super().__init__(f"User with ID {user_id} is not a captain")


class InvitationAlreadyExistsException(DomainConflictException):
    def __init__(self, user_id: UUID, team_id: UUID) -> None:
        self.user_id: UUID = user_id
        self.team_id: UUID = team_id
        super().__init__(
            f"Invitation for user {user_id} to team {team_id} already exists"
        )


class UsersNotInSameTeamException(DomainForbiddenException):
    def __init__(self, user_id: UUID) -> None:
        self.user_id: UUID = user_id
        super().__init__(
            f"User with ID {user_id} is not in the same team as the initiator"
        )


class CaptainCannotRemoveSelfException(DomainForbiddenException):
    def __init__(self, user_id: UUID) -> None:
        self.user_id: UUID = user_id
        super().__init__(
            f"Captain with ID {user_id} cannot remove themselves from the team"
        )


class CaptainCannotLeaveTeamException(DomainForbiddenException):
    def __init__(self, user_id: UUID) -> None:
        self.user_id: UUID = user_id
        super().__init__(
            f"Captain with ID {user_id} cannot leave while other members remain"
        )
