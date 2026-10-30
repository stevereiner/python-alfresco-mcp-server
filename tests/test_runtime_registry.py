"""Offline tests for runtime contracts (no live Alfresco required)."""
import pytest

from alfresco_mcp_server.discovery.registry import (
    Operation,
    Parameter,
    RuntimeRegistry,
)
from alfresco_mcp_server.discovery.transport import build_request, invoke_operation


def _get_node():
    return Operation(
        id="rest:node.get",
        method="GET",
        path="/alfresco/api/-default-/public/alfresco/versions/1/nodes/{nodeId}",
        source="runtime",
        parameters=(Parameter("nodeId", location="path", required=True),),
        executable=True,
        effect="read",
    )


def test_typed_template_validation():
    op = _get_node()
    assert build_request(op, {"nodeId": "a-123"})[0].endswith("/a-123")
    with pytest.raises(ValueError):
        build_request(op, {"nodeId": "../admin"})
    with pytest.raises(ValueError):
        build_request(op, {"wrong": "a-123"})
    with pytest.raises(ValueError):
        build_request(op, {})


def test_refuse_arbitrary_http_url():
    with pytest.raises(ValueError):
        Operation("webscript:evil", "GET", "https://evil.example/", "runtime")
    with pytest.raises(ValueError):
        Operation("webscript:evil", "GET", "/alfresco/../../etc", "runtime")


def test_require_explicit_path_contract():
    with pytest.raises(ValueError):
        Operation(
            "webscript:incomplete", "GET", "/alfresco/service/a/{id}",
            "runtime", executable=False
        )


def test_value_validation():
    op = Operation(
        id="rest:test.operation",
        method="GET",
        path="/alfresco/service/api/example",
        source="runtime",
        effect="read",
        executable=True,
        parameters=(
            Parameter("limit", kind="integer"),
            Parameter("active", kind="boolean"),
        ),
    )
    assert build_request(op, {"active": True, "limit": 3})[1] == {
        "active": "true", "limit": 3
    }
    with pytest.raises(ValueError):
        build_request(op, {"limit": True})


@pytest.mark.asyncio
async def test_refresh_replaces_removed_operations():
    catalog = RuntimeRegistry(ttl_seconds=300)
    calls = 0

    async def provider():
        nonlocal calls
        calls += 1
        return [_get_node()] if calls == 1 else []

    catalog.register_provider("fixture", provider)
    assert len(await catalog.list_operations()) == 1
    assert len(await catalog.list_operations()) == 1
    assert calls == 1
    await catalog.refresh()
    assert await catalog.list_operations() == []


@pytest.mark.asyncio
async def test_failing_provider_does_not_keep_stale_operations():
    catalog = RuntimeRegistry()
    calls = 0

    async def provider():
        nonlocal calls
        calls += 1
        if calls == 1:
            return [_get_node()]
        raise RuntimeError("offline")

    catalog.register_provider("unavailable", provider)
    assert len(await catalog.list_operations()) == 1
    summary = await catalog.refresh()
    assert summary["operations"] == 0
    assert summary["warnings"]


@pytest.mark.asyncio
async def test_mutations_denied_by_default(monkeypatch):
    monkeypatch.delenv("ALFRESCO_RUNTIME_ALLOWED_MUTATIONS", raising=False)
    operation = Operation(
        id="rest:test.delete", method="DELETE",
        path="/alfresco/api/test", source="runtime",
        executable=True, effect="mutate",
    )
    with pytest.raises(PermissionError):
        await invoke_operation(operation, {})
