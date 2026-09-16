from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import FRONTEND_URL
from .routes.auth import router as auth_router
from .routes.me import router as me_router


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


app.include_router(auth_router)
app.include_router(me_router)


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
