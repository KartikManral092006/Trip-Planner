import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


DEFAULT_ORIGINS = (
    "http://localhost:8501,http://127.0.0.1:8501,"
    "http://localhost:5173,http://127.0.0.1:5173"
)


def allowed_origins() -> list[str]:
    origins = os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS)
    return [origin.strip().rstrip("/") for origin in origins.split(",") if origin.strip()]


logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AI Travel Planner API",
    description="Multi-agent travel planner with code-checked budgets and human approval.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
