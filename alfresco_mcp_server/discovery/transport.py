"""Shared authenticated HTTP execution for runtime-discovered operations.

All paths and operation IDs originate in a validated Alfresco registry, never
in an arbitrary URL supplied by an MCP caller.
"""
from __future__ import annotations

import asyncio
import os
import re
from urllib.parse import quote, urlsplit

from .registry import Operation, Parameter
from ..utils.connection import get_core_client

_MAX_RESPONSE_BYTES = 1024 * 1024


def _validate_value(spec: Parameter, value: object) -> None:
    matches = {
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: type(v) is int,
        "number": lambda v: type(v) in (int, float),
        "boolean": lambda v: type(v) is bool,
        "array": lambda v: isinstance(v, list),
        "object": lambda v: isinstance(v, dict),
    }
    if not matches[spec.kind](value):
        raise ValueError(f"Invalid {spec.kind} value for {spec.name}")
    if spec.allowed_values and str(value) not in spec.allowed_values:
        raise ValueError(f"Unsupported value for {spec.name}")


def build_request(op: Operation, arguments: dict) -> tuple[str, dict, dict | None]:
    """Construct an encoded Alfresco-local request, rejecting unknown args."""
    if not isinstance(arguments, dict):
        raise ValueError("Arguments must be a JSON object")
    known = {p.name for p in op.parameters}
    unknown = set(arguments) - known
    if unknown:
        raise ValueError("Unknown argument(s): " + ", ".join(sorted(unknown)))
    for spec in op.parameters:
        if spec.required and (spec.name not in arguments or arguments[spec.name] is None):
            raise ValueError(f"Missing required parameter: {spec.name}")
        if spec.name in arguments and arguments[spec.name] is not None:
            _validate_value(spec, arguments[spec.name])

    path = op.path
    query: dict[str, object] = {}
    body: dict | None = None
    for spec in op.parameters:
        if spec.name not in arguments or arguments[spec.name] is None:
            continue
        value = arguments[spec.name]
        if spec.location == "path":
            string_value = str(value)
            if "/" in string_value or "\\" in string_value or string_value in (".", ".."):
                raise ValueError(f"Unsafe path argument: {spec.name}")
            path = path.replace("{" + spec.name + "}", quote(string_value, safe=""))
        elif spec.location == "query":
            if isinstance(value, (dict, list)) and not isinstance(value, list):
                raise ValueError(f"Invalid query argument: {spec.name}")
            if isinstance(value, list):
                query[spec.name] = [
                    str(v).lower() if type(v) is bool else str(v) for v in value
                ]
            else:
                query[spec.name] = str(value).lower() if type(value) is bool else value
        else:
            if body is None:
                body = {}
            body[spec.name] = value
    if re.search(r"\{[^{}]+\}", path):
        raise ValueError("Not all path parameters resolved")
    if body and op.method in ("GET", "DELETE"):
        raise ValueError("JSON body not allowed for this operation method")
    return path, query, body


def _base_url() -> str:
    url = os.getenv("ALFRESCO_URL", "http://localhost:8080").rstrip("/")
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise RuntimeError("Invalid Alfresco base URL")
    if parts.username or parts.password or parts.query or parts.fragment:
        raise RuntimeError("Alfresco base URL must not include credentials or a query")
    return f"{parts.scheme}://{parts.netloc}"


def _check_path(path: str) -> None:
    if not path.startswith("/alfresco/") or path.startswith("//"):
        raise ValueError("Only paths on the configured Alfresco service are allowed")
    if "\\" in path or any(x in (".", "..") for x in path.split("/")):
        raise ValueError("Unsafe Alfresco path")
    if re.search(r"%(?:2e|2f|5c|00)", path, re.I):
        raise ValueError("Unsafe encoded Alfresco path")


async def alfresco_request(
    method: str,
    path: str,
    *,
    params: dict | None = None,
    body: dict | None = None,
) -> dict:
    """Call configured Alfresco with the existing authenticated SDK client."""
    _check_path(path)
    if method not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
        raise ValueError("Unsupported HTTP method")
    core_client = await get_core_client()
    if not core_client.is_initialized:
        raise RuntimeError("Alfresco authenticated client is not initialized")
    client = core_client.httpx_client
    url = _base_url() + path
    try:
        response = await asyncio.to_thread(
            client.request,
            method,
            url,
            params=params or None,
            json=body,
            follow_redirects=False,
            timeout=float(os.getenv("ALFRESCO_TIMEOUT", "30")),
        )
    except Exception as exc:
        # Exceptions may contain URLs and authorization data. Keep the public
        # message deterministic and avoid echoing headers/tokens or request data.
        raise RuntimeError(f"Alfresco request failed ({type(exc).__name__})") from None
    if 300 <= response.status_code < 400:
        raise RuntimeError("Alfresco redirected the API request (check authentication)")
    if response.status_code in (401, 403):
        raise PermissionError(f"Alfresco rejected the request: HTTP {response.status_code}")
    if response.status_code >= 400:
        raise RuntimeError(f"Alfresco API returned HTTP {response.status_code}")
    if len(response.content) > _MAX_RESPONSE_BYTES:
        raise ValueError("Alfresco response exceeds the 1 MiB safety limit")
    content_type = response.headers.get("content-type", "").split(";")[0].lower()
    payload = None
    if content_type.endswith("/json") or content_type.endswith("+json"):
        try:
            payload = response.json()
        except ValueError:
            raise RuntimeError("Alfresco returned invalid JSON") from None
    elif content_type.startswith("text/") or content_type in ("application/xml", "application/xhtml+xml"):
        payload = response.text
    return {
        "status": response.status_code,
        "content_type": content_type,
        "data": payload,
        "size": len(response.content),
    }


def _is_mutation_allowed(op: Operation) -> bool:
    explicit = {
        item.strip() for item in
        os.getenv("ALFRESCO_RUNTIME_ALLOWED_MUTATIONS", "").split(",")
        if item.strip()
    }
    return op.id in explicit


async def invoke_operation(op: Operation, arguments: dict) -> dict:
    if not op.executable or op.effect == "unknown":
        raise PermissionError("Operation is discovered but not enabled for execution")
    if op.method != "GET" or op.effect != "read":
        if not _is_mutation_allowed(op):
            raise PermissionError(
                "Mutating operations require explicit ALFRESCO_RUNTIME_ALLOWED_MUTATIONS"
            )
    path, query, body = build_request(op, arguments)
    return await alfresco_request(op.method, path, params=query, body=body)
