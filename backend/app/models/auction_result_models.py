from pydantic import BaseModel


class AuctionResultResponse(BaseModel):
    success: bool
    result: str
    auction_id: str
    player_id: str
