from fastapi import APIRouter

from ..models.password_reset_models import PasswordResetRequest
from ..services.password_reset_service import reset_user_password


router = APIRouter(
    prefix="/api/password-reset",
    tags=["Password Reset"]
)


@router.post("")
def password_reset(
    data: PasswordResetRequest
):

    return reset_user_password(
        data.email,
        data.new_password
    )
