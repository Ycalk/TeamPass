from uuid import UUID

from teampass.domain_core import (
    DomainConflictException,
    DomainForbiddenException,
    DomainNotFoundException,
)


class MarketListingNotFoundException(DomainNotFoundException):
    def __init__(self, listing_id: UUID) -> None:
        self.listing_id: UUID = listing_id
        super().__init__(f"Market listing with ID {listing_id} not found")


class MarketResponseNotFoundException(DomainNotFoundException):
    def __init__(self, response_id: UUID) -> None:
        self.response_id: UUID = response_id
        super().__init__(f"Market response with ID {response_id} not found")


class MarketDealNotFoundException(DomainNotFoundException):
    def __init__(self, deal_id: UUID) -> None:
        self.deal_id: UUID = deal_id
        super().__init__(f"Market deal with ID {deal_id} not found")


class ListingsLimitReachedException(DomainForbiddenException):
    def __init__(self, team_id: UUID, limit: int) -> None:
        self.team_id: UUID = team_id
        self.limit: int = limit
        super().__init__(
            f"Team {team_id} has reached the listings limit of {limit} per cycle"
        )


class NoActiveGameCycleException(DomainNotFoundException):
    def __init__(self) -> None:
        super().__init__("No active game cycle found")


class UserNotInTeamException(DomainForbiddenException):
    def __init__(self, user_id: UUID) -> None:
        self.user_id: UUID = user_id
        super().__init__(f"User with ID {user_id} is not in a team")


class DealCreationForbiddenException(DomainForbiddenException):
    def __init__(self, user_id: UUID, listing_id: UUID) -> None:
        self.user_id: UUID = user_id
        self.listing_id: UUID = listing_id
        super().__init__(
            f"User {user_id} is not allowed to create a deal for listing {listing_id}: "
            + "only members of the listing's team can do so"
        )


class DealCompletionForbiddenException(DomainForbiddenException):
    def __init__(self, user_id: UUID, deal_id: UUID) -> None:
        self.user_id: UUID = user_id
        self.deal_id: UUID = deal_id
        super().__init__(
            f"User {user_id} is not allowed to complete deal {deal_id}: "
            + "only members of the listing's team can do so"
        )


class ReportAlreadyExistsException(DomainConflictException):
    def __init__(self, deal_id: UUID) -> None:
        self.deal_id: UUID = deal_id
        super().__init__(f"A report already exists for deal {deal_id}")


class ReportUpdateForbiddenException(DomainForbiddenException):
    def __init__(self, user_id: UUID, deal_id: UUID) -> None:
        self.user_id: UUID = user_id
        self.deal_id: UUID = deal_id
        super().__init__(
            f"User {user_id} is not allowed to update the report for deal {deal_id}: "
            + "only members of the responding team can do so"
        )


class ListingClosedException(DomainForbiddenException):
    def __init__(self, listing_id: UUID):
        self.listing_id: UUID = listing_id
        super().__init__(
            f"Listing {self.listing_id} is closed and response cannot be created"
        )
