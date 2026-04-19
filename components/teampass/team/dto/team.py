from typing import Self
from uuid import UUID

from pydantic import BaseModel
from teampass.team.storage import Team as TeamPersistent
from teampass.team.storage import TeamInvitation as TeamInvitationPersistent
from teampass.user.dto import User


class Team(BaseModel):
    id: UUID
    name: str
    members: list[User]
    captain: User | None

    @classmethod
    def from_persistent(cls, team: TeamPersistent) -> Self:
        return cls(
            id=team.id,
            name=team.name,
            members=[User.from_persistent(member) for member in team.members],
            captain=User.from_persistent(team.captain) if team.captain else None,
        )


class TeamInvitation(BaseModel):
    id: UUID
    user: User
    team: Team
    accepted_at: int | None

    @classmethod
    def from_persistent(cls, invitation: TeamInvitationPersistent) -> Self:
        return cls(
            id=invitation.id,
            user=User.from_persistent(invitation.user),
            team=Team.from_persistent(invitation.team),
            accepted_at=int(invitation.accepted_at.timestamp())
            if invitation.accepted_at
            else None,
        )
