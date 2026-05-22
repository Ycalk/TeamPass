from typing import Self
from uuid import UUID

from pydantic import BaseModel
from teampass.market.storage import (
    MarketDeal as MarketDealPersistence,
)
from teampass.market.storage import MarketDealStatus, MarketResponseStatus
from teampass.market.storage import (
    MarketListing as MarketListingPersistence,
)
from teampass.market.storage import (
    MarketResponse as MarketResponsePersistence,
)
from teampass.team.dto import Team


class MarketListing(BaseModel):
    id: UUID
    team: Team
    title: str
    description: str
    created_at: int

    @classmethod
    def from_persistent(cls, listing: MarketListingPersistence) -> Self:
        return cls(
            id=listing.id,
            team=Team.from_persistent(listing.team),
            title=listing.title,
            description=listing.description,
            created_at=int(listing.created_at.timestamp()),
        )


class MarketResponse(BaseModel):
    id: UUID
    team: Team
    market_listing_id: UUID
    status: MarketResponseStatus
    created_at: int

    @classmethod
    def from_persistent(cls, response: MarketResponsePersistence) -> Self:
        return cls(
            id=response.id,
            team=Team.from_persistent(response.team),
            market_listing_id=response.market_listing_id,
            status=response.status,
            created_at=int(response.created_at.timestamp()),
        )


class MarketDeal(BaseModel):
    id: UUID
    market_response_id: UUID
    status: MarketDealStatus

    @classmethod
    def from_persistent(cls, deal: MarketDealPersistence) -> Self:
        return cls(
            id=deal.id, market_response_id=deal.market_response_id, status=deal.status
        )


class TokensInfo(BaseModel):
    free_tokens: int
    reserved_tokens: int
