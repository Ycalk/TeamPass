from typing import ClassVar

from teampass.live_option import LiveOptionBase, OptionDef


class TransactionPolicies(LiveOptionBase):
    name: ClassVar[str] = "transaction_policies"

    max_activity_points: OptionDef[int] = OptionDef(
        description="Максимальное количество баллов активности за цикл",
        default_value=500,
    )
    max_bonus_points: OptionDef[int] = OptionDef(
        description="Максимальное количество бонусных баллов за цикл",
        default_value=100,
    )
    point_ration: OptionDef[float] = OptionDef(
        description="Соотношение баллов активности к общему количеству баллов",
        default_value=0.75,
    )
