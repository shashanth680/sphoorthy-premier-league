from fastapi import APIRouter, Depends

from ..middleware.auth import get_current_user


router = APIRouter(
    prefix="/api/me",
    tags=["User"]
)


@router.get("")
def get_my_profile(
    user: dict = Depends(get_current_user)
):

    return {
        "success": True,
        "user": user
    }
