from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from backend.auth import get_auth_dependency
from backend.config import get_settings
from backend.db import get_async_engine, get_tables_dependency
from backend.endpoints import get_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await app.extra["engine"].dispose()


def create_app(*args, **kwargs) -> FastAPI:
    settings = kwargs.get("settings") or get_settings()

    engine = get_async_engine(settings)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async def async_db_session() -> AsyncIterator[AsyncSession]:
        async with async_session() as session:
            yield session
            await session.aclose()

    tables = get_tables_dependency(settings)

    auth = get_auth_dependency(
        host=settings.auth_host,
        port=settings.auth_port,
        realm=settings.auth_realm,
        http_schema=settings.auth_http_schema,
        verify_audience=False,
    )

    app = FastAPI(engine=engine, lifespan=lifespan)

    @app.get("/backend/")
    def root():
        return {"msg": "Hello (no auth required for this endpoint)"}

    app.include_router(
        get_router(
            auth=auth,
            async_db_session=async_db_session,
            tables=tables,
        ),
        prefix="/backend",
        dependencies=[Depends(auth)]
    )

    return app


if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
