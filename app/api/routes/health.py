from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", summary="Health check")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/database", summary="Check database connectivity")
def database_health() -> dict[str, object]:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"database": "connected", "result": result.scalar()}
