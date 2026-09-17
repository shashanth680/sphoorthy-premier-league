from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from ..supabase_client import supabase


def get_settings():

    response = (
        supabase
        .table("auction_settings")
        .select("*")
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Auction settings not found"
        )

    return response.data[0]


def get_current_auction():

    response = (
        supabase
        .table("auctions")
        .select("*")
        .in_(
            "status",
            [
                "LIVE",
                "PAUSED",
                "AWAITING_SOLD"
            ]
        )
        .order(
            "updated_at",
            desc=True
        )
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    auction = response.data[0]


    # Get safe player information
    # Mobile number is intentionally NOT selected.
    player_response = (
        supabase
        .table("players")
        .select(
            "id, name, department, role, "
            "base_price, photo_url"
        )
        .eq(
            "id",
            auction["player_id"]
        )
        .single()
        .execute()
    )

    player = player_response.data


    # Get safe highest-bidding team information
    team = None

    if auction["highest_team_id"]:

        team_response = (
            supabase
            .table("teams")
            .select(
                "id, name, short_name, "
                "logo_url, jersey_color"
            )
            .eq(
                "id",
                auction["highest_team_id"]
            )
            .single()
            .execute()
        )

        team = team_response.data


    return {
        "id": auction["id"],
        "player_id": auction["player_id"],
        "status": auction["status"],
        "current_bid": auction["current_bid"],
        "highest_team_id": auction[
            "highest_team_id"
        ],
        "started_at": auction["started_at"],
        "ends_at": auction["ends_at"],
        "updated_at": auction["updated_at"],

        "player_name": (
            player["name"]
            if player
            else None
        ),

        "department": (
            player["department"]
            if player
            else None
        ),

        "role": (
            player["role"]
            if player
            else None
        ),

        "base_price": (
            player["base_price"]
            if player
            else None
        ),

        "player_photo_url": (
            player["photo_url"]
            if player
            else None
        ),

        "highest_team_name": (
            team["name"]
            if team
            else None
        ),

        "highest_team_short_name": (
            team["short_name"]
            if team
            else None
        ),

        "highest_team_logo_url": (
            team["logo_url"]
            if team
            else None
        ),

        "highest_team_jersey_color": (
            team["jersey_color"]
            if team
            else None
        )
    }


def start_auction(player_id: str):

    # Make sure there isn't already an active auction
    current = get_current_auction()

    if current:
        raise HTTPException(
            status_code=400,
            detail="Another auction is already active"
        )

    # Get player
    player_response = (
        supabase
        .table("players")
        .select("*")
        .eq("id", player_id)
        .single()
        .execute()
    )

    player = player_response.data

    if not player:
        raise HTTPException(
            status_code=404,
            detail="Player not found"
        )

    if player["status"] != "AVAILABLE":
        raise HTTPException(
            status_code=400,
            detail="Player is not available for auction"
        )

    if player["base_price"] is None:
        raise HTTPException(
            status_code=400,
            detail="Base price has not been assigned"
        )

    settings = get_settings()

    now = datetime.now(timezone.utc)

    ends_at = now + timedelta(
        seconds=settings["initial_timer_seconds"]
    )

    # Create auction
    auction_response = (
        supabase
        .table("auctions")
        .insert({
            "player_id": player_id,
            "status": "LIVE",
            "current_bid": player["base_price"],
            "highest_team_id": None,
            "started_at": now.isoformat(),
            "ends_at": ends_at.isoformat()
        })
        .execute()
    )

    if not auction_response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to start auction"
        )

    # Change player status
    supabase \
        .table("players") \
        .update({
            "status": "LIVE"
        }) \
        .eq("id", player_id) \
        .execute()

    return auction_response.data[0]


def get_auction(auction_id: str):

    response = (
        supabase
        .table("auctions")
        .select(
            "*, players(*), teams(*)"
        )
        .eq("id", auction_id)
        .single()
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Auction not found"
        )

    return response.data
