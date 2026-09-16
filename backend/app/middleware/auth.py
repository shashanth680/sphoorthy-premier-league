from fastapi import Header, HTTPException

from ..supabase_client import supabase


def get_current_user(
    authorization: str = Header(...)
):
    """
    Validate the Supabase access token and
    return the authenticated user's profile.
    """

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format"
        )

    token = authorization.split(" ", 1)[1]

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Access token is missing"
        )

    try:
        user_response = supabase.auth.get_user(token)

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token"
        )

    user = user_response.user

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    profile_response = (
        supabase
        .table("profiles")
        .select(
            "id, full_name, role, team_id"
        )
        .eq("id", user.id)
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
        "id": user.id,
        "email": user.email,
        "full_name": profile["full_name"],
        "role": profile["role"],
        "team_id": profile["team_id"]
    }


def require_admin(user: dict):
    """
    Allow only admin users.
    """

    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return user


def require_franchise(user: dict):
    """
    Allow only franchise users.
    """

    if user["role"] != "franchise":
        raise HTTPException(
            status_code=403,
            detail="Franchise access required"
        )

    if not user["team_id"]:
        raise HTTPException(
            status_code=403,
            detail="Franchise is not assigned to a team"
        )

    return user
