from typing import ClassVar

from teampass.live_option import LiveOptionBase, OptionDef


class MarketPolicies(LiveOptionBase):
    name: ClassVar[str] = "market_policies"

    listings_limit: OptionDef[int] = OptionDef(
        description="Максимальное количество запросов за цикл",
        default_value=3,
    )
    market_points: OptionDef[int] = OptionDef(
        description="Начисление бонусных баллов за выполнение запроса на бирже знаний",
        default_value=40,
    )
