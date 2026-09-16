from pydantic import BaseModel, Field


class PlayerCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )

    roll_number: str | None = None

    department: str | None = None

    year: str | None = None

    role: str | None = None

    batting_style: str | None = None

    bowling_style: str | None = None

    photo_url: str | None = None

    base_price: float | None = Field(
    default=None,
    ge=0
)


class PlayerUpdate(BaseModel):
    name: str | None = None

    roll_number: str | None = None

    department: str | None = None

    year: str | None = None

    role: str | None = None

    batting_style: str | None = None

    bowling_style: str | None = None

    photo_url: str | None = None

    base_price: float = Field(
        default=10000,
        ge=0
    )


class PlayerResponse(BaseModel):
    id: str
    name: str
    roll_number: str | None
    department: str | None
    year: str | None
    role: str | None
    batting_style: str | None
    bowling_style: str | None
    photo_url: str | None
    base_price: float
    status: str
