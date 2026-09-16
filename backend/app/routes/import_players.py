from fastapi import APIRouter, Depends, File, UploadFile

from ..middleware.auth import (
    get_current_user,
    require_admin
)

from ..services.import_service import (
    import_players
)


router = APIRouter(
    prefix="/api/import",
    tags=["Player Import"]
)


@router.post("/players")
async def upload_players(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):

    require_admin(user)

    if not file.filename:
        return {
            "success": False,
            "message": "No file selected"
        }

    filename = file.filename.lower()

    if not filename.endswith(
        (".csv", ".xlsx", ".xls")
    ):
        return {
            "success": False,
            "message": "Only CSV and Excel files are supported"
        }

    file_bytes = await file.read()

    if not file_bytes:
        return {
            "success": False,
            "message": "Uploaded file is empty"
        }

    result = import_players(
        file_bytes,
        file.filename
    )

    return result
