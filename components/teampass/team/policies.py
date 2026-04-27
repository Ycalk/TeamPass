from typing import ClassVar

from teampass.live_option import LiveOptionBase, OptionDef


class TeamPolicies(LiveOptionBase):
    name: ClassVar[str] = "team_policies"

    max_users: OptionDef[int] = OptionDef(
        description="Максимальное количество студентов в команде", default_value=6
    )
    allow_team_transfers: OptionDef[bool] = OptionDef(
        description="Разрешены переходы между командами", default_value=True
    )
