"""Bounded HTTP access for the opt-in document tools.

Reuse the SDK's authenticated client, including request-local identity when
provided by the connection layer. Never accept a caller-supplied host/token.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Any
from urllib.parse import urlsplit

_ID = re.compile(r"[A-Za-z0-9_-]{1,200}\Z")
JSON_LIMIT = 2 * 1024 * 1024


def node_id(value: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError("Expected an Alfresco node ID or a supported alias, not a URL/path")
    return value


def filename(value: str) -> str:
    if (not isinstance(value, str) or not value or len(value) > 255
            or value in (".", "..") or value[-1] in " ."
            or any(ord(c) < 32 or c in '<>:"/\\|?*' for c in value)):
        raise ValueError("Expected a filename without directories or reserved characters")
    return value


def byte_limit() -> int:
    """Fail closed on bad configuration; cap inline transfers at 16 MiB."""
    try:
        limit = min(int(os.getenv("MAX_FILE_SIZE", "100000000")),
                    int(os.getenv("MCP_DOCUMENT_MAX_BYTES", "10485760")))
    except ValueError:
        raise ValueError("Document byte limits must be integers") from None
    if not 1 <= limit <= 16 * 1024 * 1024:
        raise ValueError("Effective document byte limit must be between 1 and 16777216")
    return limit


def require_writes() -> None:
    if os.getenv("MCP_DOCUMENT_WRITES_ENABLED", "false").strip().lower() != "true":
        raise PermissionError("New document write tools require MCP_DOCUMENT_WRITES_ENABLED=true")


def api_root(base: str) -> str:
    parts = urlsplit(base)
    if (parts.scheme not in ("http", "https") or not parts.hostname
            or parts.username or parts.password or parts.query or parts.fragment):
        raise ValueError("ALFRESCO_URL must be an HTTP(S) repository URL without credentials/query")
    base = base.rstrip("/")
    public = "/alfresco/api/-default-/public"
    if base.endswith(public + "/alfresco/versions/1"):
        return base
    if base.endswith(public):
        return base + "/alfresco/versions/1"
    if base.endswith("/alfresco/api"):
        return base + "/-default-/public/alfresco/versions/1"
    if base.endswith("/alfresco"):
        return base + "/api/-default-/public/alfresco/versions/1"
    return base + public + "/alfresco/versions/1"


async def _client_and_root():
    # Lazy import keeps parsing/validation independently testable.
    from ...utils.connection import get_core_client, get_alfresco_config
    core = await get_core_client()
    core.ensure_httpx_client()
    return core.httpx_client, api_root(get_alfresco_config()["alfresco_url"])


def _request(client, root: str, method: str, path: str, limit: int, **kwargs) -> bytes:
    # Call sites construct paths from validated IDs and fixed route suffixes.
    if (not path.startswith("/nodes/") or any(c in path for c in "?#%\\")
            or any(p in (".", "..") for p in path.split("/"))):
        raise ValueError("Invalid document API path")
    try:
        with client.stream(method, root + path, follow_redirects=False, **kwargs) as response:
            if not 200 <= response.status_code < 300:
                # Do not expose URLs, credentials, or server response bodies.
                raise RuntimeError(f"Alfresco document request failed (HTTP {response.status_code})")
            declared = response.headers.get("content-length")
            if declared and declared.isdigit() and int(declared) > limit:
                raise ValueError("Alfresco response exceeds the configured byte limit")
            chunks: list[bytes] = []
            size = 0
            for chunk in response.iter_bytes(chunk_size=65536):
                size += len(chunk)
                if size > limit:
                    raise ValueError("Alfresco response exceeds the configured byte limit")
                chunks.append(chunk)
            return b"".join(chunks)
    except (ValueError, RuntimeError):
        raise
    except Exception:
        # Do not retry writes: a timeout can occur after Alfresco committed them.
        raise RuntimeError("Alfresco request failed; for writes, verify repository state before retrying") from None


async def request_bytes(method: str, path: str, *, limit: int, **kwargs) -> bytes:
    client, root = await _client_and_root()
    return await asyncio.to_thread(_request, client, root, method, path, limit, **kwargs)


async def request_json(method: str, path: str, **kwargs) -> dict[str, Any]:
    data = await request_bytes(method, path, limit=JSON_LIMIT, **kwargs)
    try:
        result = json.loads(data)
    except (ValueError, UnicodeError):
        raise RuntimeError("Alfresco returned an invalid JSON response") from None
    if not isinstance(result, dict):
        raise RuntimeError("Alfresco returned a non-object JSON response")
    return result


def entry(result: dict) -> dict:
    value = result.get("entry")
    if not isinstance(value, dict):
        raise RuntimeError("Alfresco response is missing a node entry")
    return value
