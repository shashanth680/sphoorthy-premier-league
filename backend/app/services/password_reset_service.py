from fastapi import HTTPException

from ..supabase_client import supabase


def reset_user_password(email: str, new_password: str):

    try:
        users_response = (
            supabase.auth.admin.list_users()
        )

        users = users_response.users

        target_user = None

        for user in users:
            if user.email and user.email.lower() == email.lower():
                target_user = user
                break

        if not target_user:
            raise HTTPException(
                status_code=404,
                detail="User with this email was not found"
            )

        supabase.auth.admin.update_user_by_id(
            target_user.id,
            {
                "password": new_password
            }
        )

        return {
            "success": True,
            "message": "Password updated successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update password: {str(e)}"
        )
