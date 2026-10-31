from fastapi import status
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import Settings
from app.database import create_warehouse_engine

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = create_warehouse_engine(Settings())
    app.state.db_engine = engine

    try:
        yield
    finally:
        await engine.dispose()



app = FastAPI(
    title="E-commerce Data Query",
    description="An English-language assistant for e-commerce data analysis.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "message": "Welcome to E-commerce Data Query."
    }


@app.get("/health")
def read_health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "e-commerce-data-query",
    }

@app.get("/health/db")
async def read_database_health(request: Request) -> dict[str, str]:
    try:
        async with request.app.state.db_engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    except SQLAlchemyError:
        logger.exception("Database health check failed")

        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        ) from None

    return {
        "status": "ok",
        "database": "reachable",
    }