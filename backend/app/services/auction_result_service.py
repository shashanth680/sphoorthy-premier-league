from fastapi import HTTPException

from ..supabase_client import supabase


def mark_sold(auction_id: str):

    try:

        response = supabase.rpc(
            "mark_auction_sold",
            {
                "p_auction_id": auction_id
            }
        ).execute()

    except Exception as error:

        message = str(error)

        if "Auction not found" in message:
            raise HTTPException(
                status_code=404,
                detail="Auction not found"
            )

        if "No team has placed a bid" in message:
            raise HTTPException(
                status_code=400,
                detail="No team has placed a bid"
            )

        if "cannot be marked sold" in message:
            raise HTTPException(
                status_code=400,
                detail="Auction cannot be marked sold"
            )

        if "squad is already full" in message:
            raise HTTPException(
                status_code=400,
                detail="Team squad is already full"
            )

        if "insufficient purse" in message.lower():
            raise HTTPException(
                status_code=400,
                detail="Team has insufficient purse"
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to mark player as sold"
        )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to mark player as sold"
        )

    return response.data


def mark_unsold(auction_id: str):

    try:

        response = supabase.rpc(
            "mark_auction_unsold",
            {
                "p_auction_id": auction_id
            }
        ).execute()

    except Exception as error:

        message = str(error)

        if "Auction not found" in message:
            raise HTTPException(
                status_code=404,
                detail="Auction not found"
            )

        if "cannot be marked unsold" in message:
            raise HTTPException(
                status_code=400,
                detail="Auction cannot be marked unsold"
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to mark player as unsold"
        )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to mark player as unsold"
        )

    return response.data
