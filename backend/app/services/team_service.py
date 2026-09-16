from fastapi import HTTPException

from ..supabase_client import supabase


def get_all_teams():

    response = (
        supabase
        .table("teams")
        .select("*")
        .order("created_at")
        .execute()
    )

    return response.data or []


def get_team(team_id: str):

    response = (
        supabase
        .table("teams")
        .select("*")
        .eq("id", team_id)
        .single()
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    return response.data


def create_team(data):

    existing = (
        supabase
        .table("teams")
        .select("id")
        .or_(
            f"name.eq.{data.name},"
            f"short_name.eq.{data.short_name}"
        )
        .execute()
    )

    if existing.data:
        raise HTTPException(
            status_code=400,
            detail="Team name or short name already exists"
        )

    team_data = {
        "name": data.name,
        "short_name": data.short_name,
        "owner_name": data.owner_name,
        "owner_email": data.owner_email,
        "purse_total": data.purse_total,
        "purse_remaining": data.purse_total,
        "max_squad_size": data.max_squad_size,
        "logo_url": data.logo_url,
        "jersey_color": data.jersey_color
    }

    response = (
        supabase
        .table("teams")
        .insert(team_data)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to create team"
        )

    return response.data[0]


def update_team(team_id: str, data):

    team = get_team(team_id)

    update_data = data.model_dump(
        exclude_none=True
    )

    if not update_data:
        return team

    # Do not automatically change the remaining
    # purse when changing purse_total.
    #
    # Purse changes will be controlled separately
    # by the auction system.

    if "purse_total" in update_data:
        del update_data["purse_total"]

    response = (
        supabase
        .table("teams")
        .update(update_data)
        .eq("id", team_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to update team"
        )

    return response.data[0]


def delete_team(team_id: str):

    get_team(team_id)

    squad = (
        supabase
        .table("squads")
        .select("id")
        .eq("team_id", team_id)
        .execute()
    )

    if squad.data:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a team with players in its squad"
        )

    profiles = (
        supabase
        .table("profiles")
        .select("id")
        .eq("team_id", team_id)
        .execute()
    )

    if profiles.data:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a team assigned to a franchise user"
        )

    response = (
        supabase
        .table("teams")
        .delete()
        .eq("id", team_id)
        .execute()
    )

    return {
        "success": True,
        "message": "Team deleted successfully"
    }
