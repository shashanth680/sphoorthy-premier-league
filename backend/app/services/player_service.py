from fastapi import HTTPException

from ..supabase_client import supabase


def get_all_players():

    response = (
        supabase
        .table("players")
        .select("*")
        .order("name")
        .execute()
    )

    return response.data or []


def get_player(player_id: str):

    response = (
        supabase
        .table("players")
        .select("*")
        .eq("id", player_id)
        .single()
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Player not found"
        )

    return response.data


def create_player(data):

    # Check duplicate roll number when provided
    if data.roll_number:

        existing = (
            supabase
            .table("players")
            .select("id")
            .eq("roll_number", data.roll_number)
            .execute()
        )

        if existing.data:
            raise HTTPException(
                status_code=400,
                detail="A player with this roll number already exists"
            )

   player_data = {
    "name": data.name,
    "roll_number": data.roll_number,
    "department": data.department,
    "year": data.year,
    "role": data.role,
    "batting_style": data.batting_style,
    "bowling_style": data.bowling_style,
    "mobile_number": data.mobile_number,
    "photo_url": data.photo_url,
    "base_price": data.base_price
}

    response = (
        supabase
        .table("players")
        .insert(player_data)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to create player"
        )

    return response.data[0]


def update_player(player_id: str, data):

    player = get_player(player_id)

    update_data = data.model_dump(
        exclude_none=True
    )

    if not update_data:
        return player

    # Auction status must be controlled
    # by the auction engine, not this endpoint.
    update_data.pop("status", None)

    response = (
        supabase
        .table("players")
        .update(update_data)
        .eq("id", player_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to update player"
        )

    return response.data[0]


def delete_player(player_id: str):

    player = get_player(player_id)

    if player["status"] != "AVAILABLE":
        raise HTTPException(
            status_code=400,
            detail="Only available players can be deleted"
        )

    response = (
        supabase
        .table("players")
        .delete()
        .eq("id", player_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete player"
        )

    return {
        "success": True,
        "message": "Player deleted successfully"
    }
