from fastapi import APIRouter, Depends

from ..middleware.auth import (
    get_current_user,
    require_admin
)

from ..models.player_models import (
    PlayerCreate,
    PlayerUpdate
)

from ..services.player_service import (
    get_all_players,
    get_player,
    create_player,
    update_player,
    delete_player
)


router = APIRouter(
    prefix="/api/players",
    tags=["Players"]
)


@router.get("")
def list_players(
    user: dict = Depends(get_current_user)
):

    return {
        "success": True,
        "players": get_all_players()
    }


@router.get("/{player_id}")
def player_details(
    player_id: str,
    user: dict = Depends(get_current_user)
):

    return {
        "success": True,
        "player": get_player(player_id)
    }


@router.post("")
def add_player(
    data: PlayerCreate,
    user: dict = Depends(get_current_user)
):

    require_admin(user)

    player = create_player(data)

    return {
        "success": True,
        "player": player
    }


@router.patch("/{player_id}")
def edit_player(
    player_id: str,
    data: PlayerUpdate,
    user: dict = Depends(get_current_user)
):

    require_admin(user)

    player = update_player(
        player_id,
        data
    )

    return {
        "success": True,
        "player": player
    }


@router.delete("/{player_id}")
def remove_player(
    player_id: str,
    user: dict = Depends(get_current_user)
):

    require_admin(user)

    return delete_player(player_id)
