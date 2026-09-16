from fastapi import HTTPException

from ..supabase_client import supabase


def create_franchise(data):

    # Check whether the team exists
    team_response = (
        supabase
        .table("teams")
        .select("id, name")
        .eq("id", data.team_id)
        .single()
        .execute()
    )

    if not team_response.data:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    # Check whether the email is already used
    existing_profile = (
        supabase
        .table("profiles")
        .select("id")
        .eq("id", "00000000-0000-0000-0000-000000000000")
        .execute()
    )

    try:
        # Create Supabase Auth user
        auth_response = (
            supabase.auth.admin.create_user({
                "email": data.email,
                "password": data.password,
                "email_confirm": True
            })
        )

    except Exception as error:
        error_message = str(error).lower()

        if "already" in error_message or "exists" in error_message:
            raise HTTPException(
                status_code=400,
                detail="An account with this email already exists"
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to create franchise account"
        )

    if not auth_response.user:
        raise HTTPException(
            status_code=500,
            detail="Failed to create franchise account"
        )

    user_id = auth_response.user.id

    try:
        # Create the profile and link it to the team
        profile_response = (
            supabase
            .table("profiles")
            .insert({
                "id": user_id,
                "full_name": data.full_name,
                "role": "franchise",
                "team_id": data.team_id
            })
            .execute()
        )

    except Exception:
        # Remove Auth user if profile creation fails
        try:
            supabase.auth.admin.delete_user(user_id)
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail="Failed to create franchise profile"
        )

    if not profile_response.data:
        try:
            supabase.auth.admin.delete_user(user_id)
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail="Failed to create franchise profile"
        )

    profile = profile_response.data[0]

    return {
        "id": user_id,
        "email": data.email,
        "full_name": profile["full_name"],
        "role": profile["role"],
        "team_id": profile["team_id"]
    }
