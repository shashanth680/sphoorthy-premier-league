from pydantic import BaseModel, EmailStr, Field


class TeamCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    short_name: str = Field(min_length=2, max_length=20)

    owner_name: str = Field(
        min_length=2,
        max_length=100
    )

    owner_email: EmailStr

    purse_total: float = Field(
        default=1000000,
        gt=0
    )

    max_squad_size: int = Field(
        default=15,
        ge=1,
        le=50
    )

    logo_url: str | None = None
    jersey_color: str | None = None


class TeamUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    owner_name: str | None = None

    purse_total: float | None = None

    max_squad_size: int | None = Field(
        default=None,
        ge=1,
        le=50
    )

    logo_url: str | None = None
    jersey_color: str | None = None


class TeamResponse(BaseModel):
    id: str
    name: str
    short_name: str | None
    owner_name: str | None
    owner_email: str | None

    purse_total: float
    purse_remaining: float

    max_squad_size: int

    logo_url: str | None
    jersey_color: str | None
