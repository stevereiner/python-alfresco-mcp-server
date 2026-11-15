"""Explicit copy/move tools; no download/re-upload fallback."""
from __future__ import annotations
from ._document_http import entry, filename, node_id, request_json, require_writes


async def _relocate(action: str, source: str, target: str, name: str | None) -> dict:
    source, target = node_id(source), node_id(target)
    body = {"targetParentId": target}
    if name is not None:
        body["name"] = filename(name)
    require_writes()
    result = await request_json("POST", f"/nodes/{source}/{action}", json=body)
    return {"operation": action, "entry": entry(result)}


async def copy_node(node_id: str, target_parent_id: str, name: str | None = None) -> dict:
    """Copy a node using Alfresco's native copy API. Requires document writes enabled.

    A name conflict is reported, not silently renamed. Do not retry after an
    ambiguous network error without checking whether the copy already exists.
    """
    return await _relocate("copy", node_id, target_parent_id, name)


async def move_node(node_id: str, target_parent_id: str, name: str | None = None) -> dict:
    """Move a node using Alfresco's native move API. Requires document writes enabled.

    This changes repository location; Alfresco enforces the caller's permissions.
    """
    return await _relocate("move", node_id, target_parent_id, name)


def register(mcp) -> None:
    mcp.tool(name="copy_node", annotations={"readOnlyHint": False, "destructiveHint": False,
             "idempotentHint": False})(copy_node)
    mcp.tool(name="move_node", annotations={"readOnlyHint": False, "destructiveHint": True,
             "idempotentHint": False})(move_node)
