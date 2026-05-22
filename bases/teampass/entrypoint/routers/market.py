from typing import Final
from uuid import UUID

import structlog
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status
from opentelemetry import trace
from teampass.entrypoint.exceptions import CustomHTTPException
from teampass.entrypoint.scheme import ErrorResponse
from teampass.entrypoint.security import get_current_user_id
from teampass.market import (
    CompleteDealCommand,
    CompleteDealMethod,
    CreateDealCommand,
    CreateDealMethod,
    CreateDealPayload,
    CreateDealReportCommand,
    CreateDealReportMethod,
    CreateDealReportPayload,
    CreateListingCommand,
    CreateListingMethod,
    CreateListingPayload,
    CreateResponseCommand,
    CreateResponseMethod,
    CreateResponsePayload,
    MarketDeal,
    MarketListing,
    MarketPolicies,
    MarketResponse,
    TokensInfo,
    UpdateDealReportCommand,
    UpdateDealReportMethod,
    UpdateDealReportPayload,
)
from teampass.market.storage import (
    MarketDealDAO,
    MarketDealLoadEnum,
    MarketListingDAO,
    MarketListingLoadEnum,
    MarketResponseDAO,
    MarketResponseLoadEnum,
)
from teampass.report.methods import GetReportCommand, GetReportMethod
from teampass.transaction.methods import GetCurrentCycleMethod
from teampass.user.storage import UserDAO, UserLoadEnum

_logger: Final[structlog.BoundLogger] = structlog.get_logger(__name__)

router = APIRouter(
    prefix="/market",
    tags=["market"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Не валидный access токен",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Ресурс не найден",
        },
    },
    route_class=DishkaRoute,
)


# ========== Блок запросов (listings) ==========


@router.get("/listings", status_code=status.HTTP_200_OK)
async def get_all_listings(
    listing_dao: FromDishka[MarketListingDAO],
    user_id: UUID = Depends(get_current_user_id),
) -> list[MarketListing]:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_get_all_listings_request")

    listings = await listing_dao.find_without_deals(
        includes=[MarketListingLoadEnum.TEAM]
    )
    logger.info("get_all_listings_request_processed", count=len(listings))
    return [MarketListing.from_persistent(listing) for listing in listings]


@router.get("/listings/my", status_code=status.HTTP_200_OK)
async def get_my_team_listings(
    listing_dao: FromDishka[MarketListingDAO],
    user_dao: FromDishka[UserDAO],
    user_id: UUID = Depends(get_current_user_id),
) -> list[MarketListing]:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_get_my_team_listings_request")

    user = await user_dao.find_by_id(user_id, includes=[UserLoadEnum.TEAM])
    if user is None:
        logger.error("user_not_found")
        raise CustomHTTPException(
            error="UserNotFound",
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if user.team_id is None:
        logger.error("user_has_no_team")
        raise CustomHTTPException(
            error="UserNotInTeam",
            message="User is not in a team",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    listings = await listing_dao.find_by_team_id(
        user.team_id, includes=[MarketListingLoadEnum.TEAM]
    )
    logger.info("get_my_team_listings_request_processed", count=len(listings))
    return [MarketListing.from_persistent(listing) for listing in listings]


@router.get("/listings/tokens", status_code=status.HTTP_200_OK)
async def get_tokens_info(
    listing_dao: FromDishka[MarketListingDAO],
    user_dao: FromDishka[UserDAO],
    get_current_cycle: FromDishka[GetCurrentCycleMethod],
    policies: FromDishka[MarketPolicies],
    user_id: UUID = Depends(get_current_user_id),
) -> TokensInfo:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_get_tokens_info_request")

    user = await user_dao.find_by_id(user_id, includes=[UserLoadEnum.TEAM])
    if user is None:
        logger.error("user_not_found")
        raise CustomHTTPException(
            error="UserNotFound",
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if user.team_id is None:
        logger.error("user_has_no_team")
        raise CustomHTTPException(
            error="UserNotInTeam",
            message="User is not in a team",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    cycle = await get_current_cycle(None)
    if cycle is None:
        logger.error("no_active_game_cycle")
        raise CustomHTTPException(
            error="NoActiveGameCycle",
            message="No active game cycle found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    completed = await listing_dao.count_completed_by_team_and_cycle(
        team_id=user.team_id, game_cycle_id=cycle.id
    )
    reserved = await listing_dao.count_without_deals_by_team_and_cycle(
        team_id=user.team_id, game_cycle_id=cycle.id
    )
    free = policies.listings_limit - (completed + reserved)

    logger.info(
        "get_tokens_info_request_processed",
        free_tokens=free,
        reserved_tokens=reserved,
    )
    return TokensInfo(free_tokens=free, reserved_tokens=reserved)


@router.get("/listings/{listing_id}", status_code=status.HTTP_200_OK)
async def get_listing(
    listing_dao: FromDishka[MarketListingDAO],
    listing_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> MarketListing:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    span.set_attribute("listing.id", str(listing_id))
    logger = _logger.bind(user_id=str(user_id), listing_id=str(listing_id))
    logger.info("processing_get_listing_request")

    listing = await listing_dao.find_by_id(
        listing_id, includes=[MarketListingLoadEnum.TEAM]
    )
    if listing is None:
        logger.error("listing_not_found")
        raise CustomHTTPException(
            error="MarketListingNotFound",
            message="Market listing not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    logger.info("get_listing_request_processed")
    return MarketListing.from_persistent(listing)


@router.post(
    "/listings",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": (
                "Пользователь не состоит в команде / достигнут лимит запросов"
            ),
        },
    },
)
async def create_listing(
    method: FromDishka[CreateListingMethod],
    payload: CreateListingPayload,
    user_id: UUID = Depends(get_current_user_id),
) -> MarketListing:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_create_listing_request")

    res = await method(CreateListingCommand(user_id=user_id, **payload.model_dump()))
    logger.info("create_listing_request_processed")
    return res


# ========== Блок откликов (responses) ==========


@router.get("/responses/my", status_code=status.HTTP_200_OK)
async def get_my_responses(
    response_dao: FromDishka[MarketResponseDAO],
    user_dao: FromDishka[UserDAO],
    user_id: UUID = Depends(get_current_user_id),
) -> list[MarketResponse]:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_get_my_responses_request")

    user = await user_dao.find_by_id(user_id, includes=[UserLoadEnum.TEAM])
    if user is None:
        logger.error("user_not_found")
        raise CustomHTTPException(
            error="UserNotFound",
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if user.team_id is None:
        logger.error("user_has_no_team")
        raise CustomHTTPException(
            error="UserNotInTeam",
            message="User is not in a team",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    responses = await response_dao.find_by_team_id(
        user.team_id, includes=[MarketResponseLoadEnum.TEAM]
    )
    logger.info("get_my_responses_request_processed", count=len(responses))
    return [MarketResponse.from_persistent(response) for response in responses]


@router.get(
    "/listings/{listing_id}/responses",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": (
                "Доступ запрещен: только автор запроса может просматривать отклики"
            ),
        },
    },
)
async def get_listing_responses(
    listing_dao: FromDishka[MarketListingDAO],
    response_dao: FromDishka[MarketResponseDAO],
    user_dao: FromDishka[UserDAO],
    listing_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> list[MarketResponse]:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    span.set_attribute("listing.id", str(listing_id))
    logger = _logger.bind(user_id=str(user_id), listing_id=str(listing_id))
    logger.info("processing_get_listing_responses_request")

    user = await user_dao.find_by_id(user_id, includes=[UserLoadEnum.TEAM])
    if user is None:
        logger.error("user_not_found")
        raise CustomHTTPException(
            error="UserNotFound",
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    listing = await listing_dao.find_by_id(listing_id)
    if listing is None:
        logger.error("listing_not_found")
        raise CustomHTTPException(
            error="MarketListingNotFound",
            message="Market listing not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if user.team_id is None or user.team_id != listing.team_id:
        logger.error("access_forbidden")
        raise CustomHTTPException(
            error="AccessForbidden",
            message="Only the listing author can view responses",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    responses = await response_dao.find_by_listing_id(
        listing_id, includes=[MarketResponseLoadEnum.TEAM]
    )
    logger.info("get_listing_responses_request_processed", count=len(responses))
    return [MarketResponse.from_persistent(response) for response in responses]


@router.post(
    "/responses",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Пользователь не состоит в команде / запрос закрыт",
        },
    },
)
async def create_response(
    method: FromDishka[CreateResponseMethod],
    payload: CreateResponsePayload,
    user_id: UUID = Depends(get_current_user_id),
) -> MarketResponse:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_create_response_request")

    res = await method(CreateResponseCommand(user_id=user_id, **payload.model_dump()))
    logger.info("create_response_request_processed")
    return res


# ========== Блок сделок (deals) ==========


@router.get(
    "/listings/{listing_id}/deal",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Доступ запрещен",
        },
    },
)
async def get_deal_by_listing(
    deal_dao: FromDishka[MarketDealDAO],
    user_dao: FromDishka[UserDAO],
    listing_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> MarketDeal:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    span.set_attribute("listing.id", str(listing_id))
    logger = _logger.bind(user_id=str(user_id), listing_id=str(listing_id))
    logger.info("processing_get_deal_by_listing_request")

    user = await user_dao.find_by_id(user_id, includes=[UserLoadEnum.TEAM])
    if user is None:
        logger.error("user_not_found")
        raise CustomHTTPException(
            error="UserNotFound",
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    deal = await deal_dao.find_by_listing_id(
        listing_id, includes=[MarketDealLoadEnum.MARKET_RESPONSE]
    )
    if deal is None:
        logger.error("deal_not_found")
        raise CustomHTTPException(
            error="MarketDealNotFound",
            message="Market deal not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    listing_team_id = deal.market_response.market_listing.team_id
    response_team_id = deal.market_response.team_id
    if user.team_id is None or (
        user.team_id != listing_team_id and user.team_id != response_team_id
    ):
        logger.error("access_forbidden")
        raise CustomHTTPException(
            error="AccessForbidden",
            message="Access forbidden",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    logger.info("get_deal_by_listing_request_processed")
    return MarketDeal.from_persistent(deal)


@router.get(
    "/responses/{response_id}/deal",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Доступ запрещен",
        },
    },
)
async def get_deal_by_response(
    deal_dao: FromDishka[MarketDealDAO],
    user_dao: FromDishka[UserDAO],
    response_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> MarketDeal:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    span.set_attribute("response.id", str(response_id))
    logger = _logger.bind(user_id=str(user_id), response_id=str(response_id))
    logger.info("processing_get_deal_by_response_request")

    user = await user_dao.find_by_id(user_id, includes=[UserLoadEnum.TEAM])
    if user is None:
        logger.error("user_not_found")
        raise CustomHTTPException(
            error="UserNotFound",
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    deal = await deal_dao.find_by_response_id(
        response_id, includes=[MarketDealLoadEnum.MARKET_RESPONSE]
    )
    if deal is None:
        logger.error("deal_not_found")
        raise CustomHTTPException(
            error="MarketDealNotFound",
            message="Market deal not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    listing_team_id = deal.market_response.market_listing.team_id
    response_team_id = deal.market_response.team_id
    if user.team_id is None or (
        user.team_id != listing_team_id and user.team_id != response_team_id
    ):
        logger.error("access_forbidden")
        raise CustomHTTPException(
            error="AccessForbidden",
            message="Access forbidden",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    logger.info("get_deal_by_response_request_processed")
    return MarketDeal.from_persistent(deal)


@router.get(
    "/deals/{deal_id}/report",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Доступ запрещен",
        },
    },
)
async def get_deal_report(
    deal_dao: FromDishka[MarketDealDAO],
    user_dao: FromDishka[UserDAO],
    get_report: FromDishka[GetReportMethod],
    deal_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
):
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    span.set_attribute("deal.id", str(deal_id))
    logger = _logger.bind(user_id=str(user_id), deal_id=str(deal_id))
    logger.info("processing_get_deal_report_request")

    user = await user_dao.find_by_id(user_id, includes=[UserLoadEnum.TEAM])
    if user is None:
        logger.error("user_not_found")
        raise CustomHTTPException(
            error="UserNotFound",
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    deal = await deal_dao.find_by_id(
        deal_id, includes=[MarketDealLoadEnum.MARKET_RESPONSE]
    )
    if deal is None:
        logger.error("deal_not_found")
        raise CustomHTTPException(
            error="MarketDealNotFound",
            message="Market deal not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    listing_team_id = deal.market_response.market_listing.team_id
    response_team_id = deal.market_response.team_id
    if user.team_id is None or (
        user.team_id != listing_team_id and user.team_id != response_team_id
    ):
        logger.error("access_forbidden")
        raise CustomHTTPException(
            error="AccessForbidden",
            message="Access forbidden",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if deal.report_id is None:
        logger.error("report_not_found")
        raise CustomHTTPException(
            error="ReportNotFound",
            message="Report not found for this deal",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    report = await get_report(GetReportCommand(report_id=deal.report_id))
    logger.info("get_deal_report_request_processed")
    return report


@router.post(
    "/deals",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Пользователь не состоит в команде / доступ запрещен",
        },
    },
)
async def create_deal(
    method: FromDishka[CreateDealMethod],
    payload: CreateDealPayload,
    user_id: UUID = Depends(get_current_user_id),
) -> MarketDeal:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_create_deal_request")

    res = await method(CreateDealCommand(user_id=user_id, **payload.model_dump()))
    logger.info("create_deal_request_processed")
    return res


@router.post(
    "/deals/{deal_id}/complete",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Пользователь не состоит в команде / доступ запрещен",
        },
    },
)
async def complete_deal(
    method: FromDishka[CompleteDealMethod],
    deal_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> MarketDeal:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    span.set_attribute("deal.id", str(deal_id))
    logger = _logger.bind(user_id=str(user_id), deal_id=str(deal_id))
    logger.info("processing_complete_deal_request")

    res = await method(CompleteDealCommand(user_id=user_id, deal_id=deal_id))
    logger.info("complete_deal_request_processed")
    return res


@router.post(
    "/deals/{deal_id}/report",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Пользователь не состоит в команде / доступ запрещен",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "Репорт уже существует для этой сделки",
        },
    },
)
async def create_deal_report(
    method: FromDishka[CreateDealReportMethod],
    payload: CreateDealReportPayload,
    user_id: UUID = Depends(get_current_user_id),
) -> MarketDeal:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_create_deal_report_request")

    res = await method(CreateDealReportCommand(user_id=user_id, **payload.model_dump()))
    logger.info("create_deal_report_request_processed")
    return res


@router.patch(
    "/deals/{deal_id}/report",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Пользователь не состоит в команде / доступ запрещен",
        },
    },
)
async def update_deal_report(
    method: FromDishka[UpdateDealReportMethod],
    payload: UpdateDealReportPayload,
    user_id: UUID = Depends(get_current_user_id),
) -> MarketDeal:
    span = trace.get_current_span()
    span.set_attribute("user.id", str(user_id))
    logger = _logger.bind(user_id=str(user_id))
    logger.info("processing_update_deal_report_request")

    res = await method(UpdateDealReportCommand(user_id=user_id, **payload.model_dump()))
    logger.info("update_deal_report_request_processed")
    return res
