from pydantic import BaseModel, Field


class AuctionStart(BaseModel):
    player_id: str


class BidRequest(BaseModel):
    amount: float = Field(
        gt=0
    )


class AuctionAction(BaseModel):
    pass
