from fastapi import APIRouter

from ..models.auth_models import LoginRequest
from ..services.auth_service import login_user


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post("/login")
def login(request: LoginRequest):

    return login_user(
        request.email,
        request.password
    )
