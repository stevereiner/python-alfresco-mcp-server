"""Bounded inline upload/update for clients without access to MCP server disks."""
from __future__ import annotations
import base64
import binascii
import re
from ._document_http import byte_limit, entry, filename as check_filename, node_id as check_node_id, request_json, require_writes

_MIME = re.compile(r"[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+\Z")


def decode_content(base64_content: str | None, text_content: str | None) -> bytes:
    if (base64_content is None) == (text_content is None):
        raise ValueError("Supply exactly one of base64_content or text_content (empty content is allowed)")
    limit = byte_limit()
    if text_content is not None:
        if not isinstance(text_content, str) or len(text_content) > limit:
            raise ValueError("Text content exceeds the byte limit or is not a string")
        data = text_content.encode("utf-8")
    else:
        if not isinstance(base64_content, str) or len(base64_content) > 4 * ((limit + 2) // 3):
            raise ValueError("Base64 content exceeds the byte limit or is not a string")
        try:
            data = base64.b64decode(base64_content, validate=True)
        except (ValueError, binascii.Error):
            raise ValueError("Content must be valid, unwrapped Base64") from None
    if len(data) > limit:
        raise ValueError("Decoded content exceeds the configured byte limit")
    return data


def _mime(value: str | None, is_text: bool) -> str:
    value = value or ("text/plain" if is_text else "application/octet-stream")
    if not isinstance(value, str) or not _MIME.fullmatch(value):
        raise ValueError("Supply a MIME type without parameters or control characters")
    return value


def _metadata(value: str | None) -> str | None:
    if value is not None and (not isinstance(value, str) or len(value) > 4096):
        raise ValueError("Text metadata must contain at most 4096 characters")
    return value


async def upload_document_content(filename: str, parent_id: str = "-shared-",
                                  base64_content: str | None = None,
                                  text_content: str | None = None,
                                  mime_type: str | None = None, title: str | None = None,
                                  description: str | None = None, auto_rename: bool = False) -> dict:
    """Upload inline content with an explicit filename, without filesystem access.

    Supply exactly one content argument. Name conflicts are errors unless
    auto_rename=true. Never automatically retry an ambiguous failed upload.
    """
    filename, parent_id = check_filename(filename), check_node_id(parent_id)
    require_writes()
    content = decode_content(base64_content, text_content)
    mime = _mime(mime_type, text_content is not None)
    if type(auto_rename) is not bool:
        raise ValueError("auto_rename must be a boolean")
    form = {"name": filename, "nodeType": "cm:content",
            "autoRename": str(auto_rename).lower(), "cm:title": _metadata(title) if title is not None else filename}
    if description is not None:
        form["cm:description"] = _metadata(description)
    result = await request_json("POST", f"/nodes/{parent_id}/children", data=form,
                                files={"filedata": (filename, content, mime)})
    return {"entry": entry(result)}


async def update_document_content(node_id: str, base64_content: str | None = None,
                                  text_content: str | None = None, mime_type: str | None = None,
                                  major_version: bool = False, comment: str = "") -> dict:
    """Replace existing content from inline data and request major/minor versioning.

    Does not perform checkout/unlock, edit a binary file, or bypass repository
    locks. Verify the returned node/version before treating an update as complete.
    """
    ident = check_node_id(node_id)
    require_writes()
    content = decode_content(base64_content, text_content)
    mime = _mime(mime_type, text_content is not None)
    if type(major_version) is not bool:
        raise ValueError("major_version must be a boolean")
    _metadata(comment)
    result = await request_json("PUT", f"/nodes/{ident}/content", content=content,
        headers={"Content-Type": mime}, params={"majorVersion": str(major_version).lower(), "comment": comment})
    return {"entry": entry(result)}


def register(mcp) -> None:
    mcp.tool(name="upload_document_content", annotations={"readOnlyHint": False,
             "destructiveHint": False, "idempotentHint": False})(upload_document_content)
    mcp.tool(name="update_document_content", annotations={"readOnlyHint": False,
             "destructiveHint": True, "idempotentHint": False})(update_document_content)
