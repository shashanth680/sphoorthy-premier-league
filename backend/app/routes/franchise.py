from fastapi import APIRouter, Depends

from ..middleware.auth import (
    get_current_user,
    require_admin
)

from ..models.franchise_models import (
    FranchiseCreate
)

from ..services.franchise_service import (
    create_franchise
)


router = APIRouter(
    prefix="/api/franchise",
    tags=["Franchise"]
)


@router.post("")
def add_franchise(
    data: FranchiseCreate,
    user: dict = Depends(get_current_user)
):

    require_admin(user)

    franchise = create_franchise(data)

    return {
        "success": True,
        "franchise": franchise
    }
