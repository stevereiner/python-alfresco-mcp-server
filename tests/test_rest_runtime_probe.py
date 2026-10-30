"""REST route probes use Alfresco runtime responses, never OpenAPI files."""
import pytest

from alfresco_mcp_server.discovery import rest


@pytest.mark.asyncio
async def test_only_live_rest_routes_are_registered(monkeypatch):
    called = []

    async def fake_request(method, path):
        called.append((method, path))
        if path.endswith("/sites"):
            raise RuntimeError("HTTP 404")
        return {"status": 200, "data": {"entry": {}}, "size": 20}

    monkeypatch.setattr(rest, "alfresco_request", fake_request)
    discovered = await rest.discover_rest_capabilities()
    assert len(discovered) == len(rest._PROBES) - 1
    assert all(op.executable and op.method == "GET" for op in discovered)
    assert all(op.metadata["origin"] == "live-get-probe" for op in discovered)
    assert all(method == "GET" for method, path in called)


@pytest.mark.asyncio
async def test_not_assuming_missing_rest_routes(monkeypatch):
    async def fail(method, path):
        raise PermissionError("403")

    monkeypatch.setattr(rest, "alfresco_request", fail)
    assert await rest.discover_rest_capabilities() == []
