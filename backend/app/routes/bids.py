from fastapi import APIRouter, Depends

from ..middleware.auth import (
    get_current_user,
    require_franchise
)

from ..models.auction_models import (
    BidRequest
)

from ..services.bid_service import (
    place_bid
)


router = APIRouter(
    prefix="/api/bids",
    tags=["Bidding"]
)


@router.post("/{auction_id}")
def submit_bid(
    auction_id: str,
    data: BidRequest,
    user: dict = Depends(get_current_user)
):

    require_franchise(user)

    result = place_bid(
        auction_id=auction_id,
        team_id=user["team_id"],
        amount=data.amount
    )

    return result
