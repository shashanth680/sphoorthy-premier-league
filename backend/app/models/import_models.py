from pydantic import BaseModel


class ImportResult(BaseModel):
    success: bool
    total_rows: int
    imported: int
    skipped: int
    errors: list[str]
