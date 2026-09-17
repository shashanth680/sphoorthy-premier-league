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

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if not response.data:
        raise HTTPException(
            status_code=400,
            detail="Failed to mark auction as sold"
        )

    return {
        "success": True,
        "result": response.data
    }


def mark_unsold(auction_id: str):

    try:
        response = supabase.rpc(
            "mark_auction_unsold",
            {
                "p_auction_id": auction_id
            }
        ).execute()

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if not response.data:
        raise HTTPException(
            status_code=400,
            detail="Failed to mark auction as unsold"
        )

    return {
        "success": True,
        "result": response.data
    }
