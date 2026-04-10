from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from os import getenv
from typing import AsyncGenerator

from auth import auth_router, KEY_STORE
from database import setup_connection_pool
from routes.manage import router as manage_router
from routes.team import router as team_router
from routes.user import router as user_router
from verify.email import VERIFY_MANAGER


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await KEY_STORE.load_keys()

    async with setup_connection_pool():
        yield

app = FastAPI(
    title="HSPC 2026 Backend API",
    description="API for HSPC 2026 backend services",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in getenv("ALLOW_ORIGINS", "").split(",")
        if origin.strip()
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth_router)
app.include_router(manage_router)
app.include_router(team_router)
app.include_router(user_router)
