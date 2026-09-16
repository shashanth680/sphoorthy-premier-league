from fastapi import HTTPException

from ..supabase_client import supabase


def place_bid(
    auction_id: str,
    team_id: str,
    amount: float
):

    try:

        response = supabase.rpc(
            "place_bid",
            {
                "p_auction_id": auction_id,
                "p_team_id": team_id,
                "p_amount": amount
            }
        ).execute()

    except Exception as error:

        message = str(error)

        if "Auction not found" in message:
            raise HTTPException(
                status_code=404,
                detail="Auction not found"
            )

        if "Auction is not live" in message:
            raise HTTPException(
                status_code=400,
                detail="Auction is not live"
            )

        if "timer has expired" in message:
            raise HTTPException(
                status_code=400,
                detail="Auction timer has expired"
            )

        if "Team not found" in message:
            raise HTTPException(
                status_code=404,
                detail="Team not found"
            )

        if "squad is already full" in message:
            raise HTTPException(
                status_code=400,
                detail="Team squad is already full"
            )

        if "Insufficient purse" in message:
            raise HTTPException(
                status_code=400,
                detail="Insufficient purse"
            )

        if "Minimum bid increment" in message:
            raise HTTPException(
                status_code=400,
                detail=message
            )

        if "Bid must be higher" in message:
            raise HTTPException(
                status_code=400,
                detail=message
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to place bid"
        )

    if not response.data:

        raise HTTPException(
            status_code=500,
            detail="Failed to place bid"
        )

    return response.data
