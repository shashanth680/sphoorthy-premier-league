from datetime import datetime, timezone

from fastapi import HTTPException

from ..supabase_client import supabase
from .auction_service import get_settings


def place_bid(
    auction_id: str,
    team_id: str,
    amount: float
):

    # Get current auction
    auction_response = (
        supabase
        .table("auctions")
        .select("*")
        .eq("id", auction_id)
        .single()
        .execute()
    )

    auction = auction_response.data

    if not auction:
        raise HTTPException(
            status_code=404,
            detail="Auction not found"
        )

    # Auction must be live
    if auction["status"] != "LIVE":
        raise HTTPException(
            status_code=400,
            detail="Auction is not live"
        )

    # Check timer
    if auction["ends_at"]:

        ends_at = datetime.fromisoformat(
            auction["ends_at"].replace(
                "Z",
                "+00:00"
            )
        )

        now = datetime.now(timezone.utc)

        if now >= ends_at:

            supabase \
                .table("auctions") \
                .update({
                    "status": "AWAITING_SOLD"
                }) \
                .eq("id", auction_id) \
                .execute()

            raise HTTPException(
                status_code=400,
                detail="Auction timer has expired"
            )

    # Get team
    team_response = (
        supabase
        .table("teams")
        .select("*")
        .eq("id", team_id)
        .single()
        .execute()
    )

    team = team_response.data

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    # Check squad size
    squad_response = (
        supabase
        .table("squads")
        .select("id")
        .eq("team_id", team_id)
        .execute()
    )

    squad_count = len(
        squad_response.data or []
    )

    if squad_count >= team["max_squad_size"]:

        raise HTTPException(
            status_code=400,
            detail="Team squad is already full"
        )

    # Bid must be higher than current bid
    current_bid = auction["current_bid"]

    if amount <= current_bid:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Bid must be higher than "
                f"current bid of {current_bid}"
            )
        )

    # Check bid increment
    settings = get_settings()

    increment = settings["bid_increment"]

    if (
        amount - current_bid
    ) < increment:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Minimum bid increment is "
                f"{increment}"
            )
        )

    # Check team purse
    if amount > team["purse_remaining"]:

        raise HTTPException(
            status_code=400,
            detail="Insufficient purse"
        )

    # Save bid
    bid_response = (
        supabase
        .table("bids")
        .insert({
            "auction_id": auction_id,
            "player_id": auction["player_id"],
            "team_id": team_id,
            "amount": amount
        })
        .execute()
    )

    if not bid_response.data:

        raise HTTPException(
            status_code=500,
            detail="Failed to place bid"
        )

    # Update auction
    updated_auction = (
        supabase
        .table("auctions")
        .update({
            "current_bid": amount,
            "highest_team_id": team_id
        })
        .eq("id", auction_id)
        .execute()
    )

    if not updated_auction.data:

        raise HTTPException(
            status_code=500,
            detail="Failed to update auction"
        )

    return {
        "success": True,
        "bid": bid_response.data[0],
        "auction": updated_auction.data[0]
    }
