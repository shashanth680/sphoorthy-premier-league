from fastapi import APIRouter, Depends

from ..middleware.auth import (
    get_current_user,
    require_admin
)

from ..services.auction_result_service import (
    mark_sold,
    mark_unsold
)


router = APIRouter(
    prefix="/api/auction",
    tags=["Auction Result"]
)


@router.post("/{auction_id}/sold")
def auction_sold(
    auction_id: str,
    user: dict = Depends(get_current_user)
):

    require_admin(user)

    return mark_sold(auction_id)


@router.post("/{auction_id}/unsold")
def auction_unsold(
    auction_id: str,
    user: dict = Depends(get_current_user)
):

    require_admin(user)

    return mark_unsold(auction_id)
