from fastapi import APIRouter, Depends

from ..middleware.auth import (
    get_current_user,
    require_admin
)

from ..models.auction_models import (
    AuctionStart
)

from ..services.auction_service import (
    start_auction,
    get_current_auction,
    get_auction
)


router = APIRouter(
    prefix="/api/auction",
    tags=["Auction"]
)


@router.get("/current")
def current_auction(
    user: dict = Depends(get_current_user)
):

    return {
        "success": True,
        "auction": get_current_auction()
    }


@router.get("/{auction_id}")
def auction_details(
    auction_id: str,
    user: dict = Depends(get_current_user)
):

    return {
        "success": True,
        "auction": get_auction(auction_id)
    }


@router.post("/start")
def start_player_auction(
    data: AuctionStart,
    user: dict = Depends(get_current_user)
):

    require_admin(user)

    auction = start_auction(
        data.player_id
    )

    return {
        "success": True,
        "auction": auction
    }
