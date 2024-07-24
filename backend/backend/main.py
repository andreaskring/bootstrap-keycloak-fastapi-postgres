from contextlib import asynccontextmanager
from typing import AsyncIterator, Any

import uvicorn
from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy import text, Table, select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.util import FacadeDict

from backend.auth import get_auth_dependency
from backend.config import get_settings
from backend.db import get_async_engine, get_tables_dependency


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await app.extra["engine"].dispose()


settings = get_settings()

engine = get_async_engine(settings)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def async_db_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session
        await session.aclose()


auth = get_auth_dependency(
    host=settings.auth_host,
    port=settings.auth_port,
    realm=settings.auth_realm,
    http_schema=settings.auth_http_schema,
    verify_audience=False,
)

tables = get_tables_dependency(settings)

router = APIRouter()


@router.get("/")
def root():
    return {"msg": "Hello (no auth required for this endpoint)"}


@router.get("/require/auth")
def require_auth(token: dict[str, Any] = Depends(auth)) -> dict[str, Any]:
    return token


@router.get("/categories")
async def categories(
    db_session: AsyncSession = Depends(async_db_session),
    db_tables: FacadeDict[str, Table] = Depends(tables),
    # token: dict[str, Any] = Depends(auth),
) -> list[dict[str, str | int]]:
    stmt = select(db_tables["category"])
    result = await db_session.execute(stmt)

    return [
        {
            "id": id_,
            "name": name,
            "description": desc,
        }
        for id_, name, desc in result
    ]


@router.get("/category/{cat_id}")
async def category(
    cat_id: int,
    db_session: AsyncSession = Depends(async_db_session),
    db_tables: FacadeDict[str, Table] = Depends(tables),
    token: dict[str, Any] = Depends(auth),
) -> list[dict]:
    return []


app = FastAPI(engine=engine, lifespan=lifespan)
app.include_router(router, prefix="/backend")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
