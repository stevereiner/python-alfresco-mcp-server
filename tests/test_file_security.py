"""Regression tests for paths originating in repository metadata."""
import pytest

from alfresco_mcp_server.utils.file_security import safe_file_component, safe_node_id


@pytest.mark.parametrize("raw", ["../x", "..\\x", "bad/name.txt", "foo\\bar"])
def test_file_component_cannot_traverse(raw):
    name = safe_file_component(raw)
    assert "/" not in name
    assert "\\" not in name
    assert name not in (".", "..")


def test_reject_blank_filename():
    with pytest.raises(ValueError):
        safe_file_component(" ... ")


def test_normalize_alfresco_node_uri():
    assert safe_node_id("alfresco://workspace/abc-123") == "abc-123"


@pytest.mark.parametrize("node_id", ["../etc/passwd", "abc/123", "id?x=1", ""])
def test_reject_unsafe_node_ids(node_id):
    with pytest.raises(ValueError):
        safe_node_id(node_id)
