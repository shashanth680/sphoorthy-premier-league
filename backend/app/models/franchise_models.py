from pydantic import BaseModel, EmailStr, Field


class FranchiseCreate(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=100
    )

    full_name: str = Field(
        min_length=2,
        max_length=100
    )

    team_id: str


class FranchiseResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    team_id: str
