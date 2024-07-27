from typing import Any
from unittest.mock import patch

import pytest
from pytest import MonkeyPatch
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK
)
from pydantic import SecretStr

from backend.config import get_settings, Settings
from backend.main import create_app


NO_AUTH_ENDPOINTS = (
    "/backend/",
)


@pytest.fixture
def mock_env(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("DB_HOST", "localhost")


@pytest.fixture
def mock_settings() -> Settings:
    return get_settings(
        db_host="localhost",
        db_port=5432,
        db_name="app",
        db_user="app",
        db_password=SecretStr("secret"),
        auth_host="localhost",
        auth_port=8080,
        auth_http_schema="http",
        auth_realm="app",
        auth_client_id="app"
    )


async def mock_keycloak_auth(token: str) -> dict[str, Any]:
    return dict()


def lookup_auth_dependency(route: APIRoute) -> bool:
    # Check if auth dependency exists
    return any(d.dependency == mock_keycloak_auth for d in route.dependencies)


@patch(
    "backend.main.get_auth_dependency", return_value=mock_keycloak_auth
)
def test_ensure_endpoints_depend_on_auth_coroutine(
    # mock_get_auth_dependency: MagicMock,
    mock_settings: Settings,
) -> None:
    """
    Test that OIDC auth is enabled on all endpoints except from those
    specified in an explicit exclude list (see the NO_AUTH_ENDPOINTS)
    """

    # A little risky since we should avoid "logic" in the test code!
    # Loop through all FastAPI routes (except the ones from the above
    # exclude list) and make sure they depend on (via fastapi.Depends) the
    # auth coroutine in the auth module.

    # Arrange
    app = create_app(settings=mock_settings)

    # 1) Skip the starlette.routing.Route's (defined by the framework)
    # 2) Skip routes in the NO_AUTH_ENDPOINT
    routes = [
        route
        for route in app.routes
        if (
            isinstance(route, APIRoute) and
            route.path not in NO_AUTH_ENDPOINTS
        )
    ]

    for route in routes:
        has_auth = lookup_auth_dependency(route)
        assert has_auth, f"Route not protected: {route.path}"


def test_ensure_no_auth_endpoints_do_not_depend_on_auth_function(
    mock_settings: Settings
):
    # Arrange
    app = create_app(settings=mock_settings)

    no_auth_routes = [
        route
        for route in app.routes
        if (
            isinstance(route, APIRoute) and
            route.path in NO_AUTH_ENDPOINTS
        )
    ]
    for route in no_auth_routes:
        has_auth = lookup_auth_dependency(route)
        assert not has_auth, f"Route protected: {route.path}"


def test_root(mock_settings: Settings) -> None:
    # Arrange
    app = create_app(settings=mock_settings)
    client = TestClient(app)

    # Act
    r = client.get("/backend/")

    # Assert
    assert r.status_code == HTTP_200_OK
    assert r.json() == {"msg": "Hello (no auth required for this endpoint)"}
