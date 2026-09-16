from fastapi import APIRouter, Depends

from ..middleware.auth import (
    get_current_user,
    require_admin
)

from ..models.team_models import (
    TeamCreate,
    TeamUpdate
)

from ..services.team_service import (
    get_all_teams,
    get_team,
    create_team,
    update_team,
    delete_team
)


router = APIRouter(
    prefix="/api/teams",
    tags=["Teams"]
)


@router.get("")
def list_teams(
    user: dict = Depends(get_current_user)
):

    return {
        "success": True,
        "teams": get_all_teams()
    }


@router.get("/{team_id}")
def team_details(
    team_id: str,
    user: dict = Depends(get_current_user)
):

    return {
        "success": True,
        "team": get_team(team_id)
    }


@router.post("")
def add_team(
    data: TeamCreate,
    user: dict = Depends(get_current_user)
):

    require_admin(user)

    team = create_team(data)

    return {
        "success": True,
        "team": team
    }


@router.patch("/{team_id}")
def edit_team(
    team_id: str,
    data: TeamUpdate,
    user: dict = Depends(get_current_user)
):

    require_admin(user)

    team = update_team(
        team_id,
        data
    )

    return {
        "success": True,
        "team": team
    }


@router.delete("/{team_id}")
def remove_team(
    team_id: str,
    user: dict = Depends(get_current_user)
):

    require_admin(user)

    return delete_team(team_id)
