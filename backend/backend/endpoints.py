from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import Table, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import FacadeDict


def get_router(**kwargs) -> APIRouter:
    auth = kwargs["auth"]
    async_db_session = kwargs["async_db_session"]
    tables = kwargs["tables"]

    router = APIRouter()

    @router.get("/require/auth")
    def require_auth(token: dict[str, Any] = Depends(auth)) -> dict[str, Any]:
        # Explicit auth dependency here instead of just that included via the router,
        # since we need the token (as an example)
        return token

    @router.get("/categories")
    async def categories(
        db_session: AsyncSession = Depends(async_db_session),
        db_tables: FacadeDict[str, Table] = Depends(tables),
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
    ) -> list[dict]:
        return []

    return router
