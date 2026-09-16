from fastapi import HTTPException

from ..supabase_client import supabase


def login_user(email: str, password: str):

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not response.user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    user_id = response.user.id

    profile_response = (
        supabase
        .table("profiles")
        .select("id, full_name, role, team_id")
        .eq("id", user_id)
        .single()
        .execute()
    )

    profile = profile_response.data

    if not profile:
        raise HTTPException(
            status_code=403,
            detail="User profile not found"
        )

    return {
        "user": {
            "id": user_id,
            "email": response.user.email,
            "full_name": profile["full_name"],
            "role": profile["role"],
            "team_id": profile["team_id"]
        },
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token
    }
