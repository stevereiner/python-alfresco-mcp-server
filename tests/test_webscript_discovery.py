"""Offline fixtures for parsing the runtime Alfresco Web Script index."""
import pytest

# This provider is a targeted follow-up to the runtime Registry branch.
pytest.importorskip("alfresco_mcp_server.discovery.registry")

from alfresco_mcp_server.discovery.webscripts import parse_webscript_index


SAMPLE_INDEX = """
<html><body><h1>Registered Web Scripts</h1>
<div>GET /alfresco/service/api/myplugin/{nodeId}/metadata</div>
<div>POST /alfresco/service/myplugin/{nodeId}/process</div>
<div>GET /alfresco/service/index/all</div>
</body></html>
"""


def test_extracts_webscripts_without_static_openapi(monkeypatch):
    monkeypatch.delenv("ALFRESCO_DISCOVERY_ALLOW_UNDESCRIBED_READS", raising=False)
    found = parse_webscript_index(SAMPLE_INDEX)
    assert len(found) == 2
    assert {o.method for o in found} == {"GET", "POST"}
    assert all(not o.executable for o in found)
    assert all(o.metadata["contract"] == "incomplete" for o in found)
    assert all(o.source == "webscript-index" for o in found)


def test_path_params_are_required():
    found = parse_webscript_index(SAMPLE_INDEX)
    assert all(
        len([p for p in op.parameters if p.location == "path"]) == 1
        for op in found
    )


def test_opt_in_read_only(monkeypatch):
    monkeypatch.setenv("ALFRESCO_DISCOVERY_ALLOW_UNDESCRIBED_READS", "true")
    found = parse_webscript_index(SAMPLE_INDEX)
    assert sum(bool(o.executable) for o in found) == 1


def test_untrusted_urls_ignored():
    doc = "GET https://evil.example/fake POST /alfresco/service/../admin"
    assert parse_webscript_index(doc) == []
