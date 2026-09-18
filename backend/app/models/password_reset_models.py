from pydantic import BaseModel, EmailStr, Field


class PasswordResetRequest(BaseModel):
    email: EmailStr

    new_password: str = Field(
        min_length=8,
        max_length=100
    )
