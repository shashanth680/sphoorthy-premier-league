from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.password_reset import router as password_reset_router

from .config import FRONTEND_URL
from .routes.auth import router as auth_router
from .routes.me import router as me_router
from .routes.teams import router as teams_router
from .routes.franchise import router as franchise_router
from .routes.players import router as players_router
from .routes.import_players import router as import_players_router
from .routes.bids import router as bids_router
from .routes.auction import router as auction_router
from .routes.auction_result import (
    router as auction_result_router
)


app = FastAPI(
    title="Sphoorthy Premier League API",
    description="SPL Live Cricket Auction Backend",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(password_reset_router)
app.include_router(auth_router)
app.include_router(me_router)
app.include_router(teams_router)
app.include_router(franchise_router)
app.include_router(players_router)
app.include_router(bids_router)
app.include_router(auction_router)
app.include_router(
    auction_result_router
)


@app.get("/")
def root():

    return {
        "message": "Sphoorthy Premier League API",
        "status": "online"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }
