"""FastMCP validated bearer must never cross caller identities."""
import asyncio
import contextvars
import sys
from types import SimpleNamespace

import pytest

from alfresco_mcp_server.utils import connection


@pytest.mark.asyncio
async def test_concurrent_callers_have_distinct_clients(monkeypatch):
    token = contextvars.ContextVar("test_keycloak_token")
    created = []

    class Factory:
        def __init__(self, *, auth_util, **kwargs):
            self.token = auth_util
            created.append(self)

        def create_master_client(self):
            return SimpleNamespace(
                identity=self.token,
                core=SimpleNamespace(ensure_httpx_client=lambda: True),
            )

    monkeypatch.setitem(
        sys.modules, "python_alfresco_api", SimpleNamespace(ClientFactory=Factory)
    )
    monkeypatch.setenv("ALFRESCO_AUTH_USE_CALLER_TOKEN", "true")
    monkeypatch.setenv("ALFRESCO_AUTH_METHOD", "oauth2")
    monkeypatch.setenv("MCP_TRANSPORT_AUTH", "true")
    monkeypatch.setattr(connection, "_get_caller_bearer", token.get)
    monkeypatch.setattr(
        connection, "_build_auth_util",
        lambda config: config["oauth2"]["access_token"],
    )

    async def access(as_user):
        token.set(as_user)
        first = await connection.ensure_connection()
        await asyncio.sleep(0)
        second = await connection.ensure_connection()
        assert first is second
        factory = await connection.get_client_factory()
        assert factory.token == as_user
        return first.identity

    users = await asyncio.gather(access("user-a"), access("user-b"))
    assert users == ["user-a", "user-b"]
    assert len(created) == 2


@pytest.mark.asyncio
async def test_no_fallback_to_service_account_on_invalid_mode(monkeypatch):
    monkeypatch.setenv("ALFRESCO_AUTH_USE_CALLER_TOKEN", "true")
    monkeypatch.setenv("ALFRESCO_AUTH_METHOD", "basic")
    monkeypatch.setattr(connection, "_get_caller_bearer", lambda: "user-token")
    with pytest.raises(RuntimeError, match="oauth2"):
        await connection.ensure_connection()


def test_passthrough_rejects_transport_auth_disabled(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT_AUTH", "false")
    with pytest.raises(PermissionError, match="MCP_TRANSPORT_AUTH"):
        connection._get_caller_bearer()
