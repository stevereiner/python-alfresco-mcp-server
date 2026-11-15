"""Explicit, structured folder pagination without changing the legacy tool."""
from __future__ import annotations
from ._document_http import node_id, request_json

_ORDERS = {f"{key} {direction}" for key in ("name", "createdAt", "modifiedAt")
           for direction in ("ASC", "DESC")}


async def browse_repository_page(parent_id: str = "-my-", skip_count: int = 0,
                                 max_items: int = 25, order_by: str = "name ASC") -> dict:
    """List one folder page with pagination metadata and the next offset.

    Use next_skip_count until it is null. This is not an atomic snapshot:
    concurrent changes in the repository can alter subsequent pages.
    """
    parent_id = node_id(parent_id)
    if type(skip_count) is not int or not 0 <= skip_count <= 2147483647:
        raise ValueError("skip_count must be a nonnegative 32-bit integer")
    if type(max_items) is not int or not 1 <= max_items <= 1000:
        raise ValueError("max_items must be between 1 and 1000")
    if order_by not in _ORDERS:
        raise ValueError("order_by must be name/createdAt/modifiedAt followed by ASC or DESC")
    result = await request_json("GET", f"/nodes/{parent_id}/children", params={
        "skipCount": skip_count, "maxItems": max_items, "orderBy": order_by,
        "include": "properties,path",
    })
    listing = result.get("list")
    if not isinstance(listing, dict) or not isinstance(listing.get("entries"), list):
        raise RuntimeError("Alfresco response is missing a folder listing")
    page = listing.get("pagination")
    if not isinstance(page, dict) or type(page.get("hasMoreItems")) is not bool:
        raise RuntimeError("Alfresco response is missing pagination metadata")
    offset, count = page.get("skipCount"), page.get("count")
    if (type(offset) is not int or offset < 0 or type(count) is not int or count < 0
            or count != len(listing["entries"]) or (page["hasMoreItems"] and count == 0)):
        raise RuntimeError("Alfresco returned inconsistent pagination metadata")
    return {"parent_id": parent_id, "entries": listing["entries"], "pagination": page,
            "next_skip_count": offset + count if page["hasMoreItems"] else None}


def register(mcp) -> None:
    mcp.tool(name="browse_repository_page", annotations={"readOnlyHint": True,
             "destructiveHint": False, "idempotentHint": True})(browse_repository_page)
