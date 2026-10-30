"""Runtime Web Script index adapter for Alfresco.

This module is activated by the core runtime registry when installed. It
requires the registry feature branch to have been merged first. It never
executes indexed scripts as part of discovery and does not import OpenAPI.
"""
from __future__ import annotations

import hashlib
import html
import os
import re
from html.parser import HTMLParser

from .registry import Operation, Parameter, registry
from .transport import alfresco_request

# The Web Script Index is an introspection source, not an invocation contract.
_INDEX_PATHS = (
    "/alfresco/service/index/all",
    "/alfresco/service/index",
)
_ROUTE = re.compile(
    r"\b(GET|POST|PUT|PATCH|DELETE)\s+"
    r"(/(?:alfresco/(?:service|s|wcs|api)|service|api)/[^\s<>'\"?#]+)",
    re.IGNORECASE,
)
_PLACEHOLDER = re.compile(r"\{([A-Za-z][A-Za-z0-9_-]*)\}")


class _IndexText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        self.chunks.append(data)

    def text(self) -> str:
        return " ".join(self.chunks)


def _normalize_path(path: str) -> str:
    if path.startswith("/api/") or path.startswith("/service/"):
        path = "/alfresco/service" + path
    return path.rstrip("/")


def parse_webscript_index(document: str) -> list[Operation]:
    """Extract method/URI templates from Alfresco's live index (best effort).

    Never infer required query/body parameters from text. For incomplete
    Web Script contracts, execution is disabled by default.
    """
    if not isinstance(document, str):
        raise ValueError("Web Script index must be text")
    reader = _IndexText()
    reader.feed(document)
    # Search both markup-stripped text and raw HTML: index pages vary by
    # Alfresco release, and certain templates appear in anchor attributes.
    texts = (html.unescape(document), reader.text())
    operations: dict[str, Operation] = {}
    allow_unverified_get = (
        os.getenv("ALFRESCO_DISCOVERY_ALLOW_UNDESCRIBED_READS", "false").lower()
        == "true"
    )
    for text in texts:
        for match in _ROUTE.finditer(text):
            method = match.group(1).upper()
            path = _normalize_path(match.group(2))
            if "/index/" in path or path.endswith("/index"):
                continue
            identifiers = tuple(dict.fromkeys(_PLACEHOLDER.findall(path)))
            params = tuple(
                Parameter(name=name, location="path", required=True)
                for name in identifiers
            )
            digest = hashlib.sha256((method + " " + path).encode()).hexdigest()[:16]
            operation_id = "webscript:runtime." + digest
            try:
                op = Operation(
                    id=operation_id,
                    method=method,
                    path=path,
                    source="webscript-index",
                    description=f"Discovered Web Script: {method} {path}",
                    parameters=params,
                    # The index does not guarantee a complete parameter schema.
                    executable=allow_unverified_get and method == "GET",
                    effect="read" if method == "GET" else "unknown",
                    metadata={
                        "contract": "incomplete",
                        "origin": "alfresco-webscript-index",
                        "execution_note": (
                            "Set ALFRESCO_DISCOVERY_ALLOW_UNDESCRIBED_READS=true "
                            "to opt into GETs without full query-contract metadata"
                        ),
                    },
                )
            except ValueError:
                # Ignore malformed URL templates rather than converting them
                # to potentially unsafe URLs.
                continue
            operations[operation_id] = op
            if len(operations) >= 250:
                break
    return list(operations.values())


async def discover_webscripts() -> list[Operation]:
    errors = []
    for path in _INDEX_PATHS:
        try:
            result = await alfresco_request("GET", path)
            content = result["data"]
            if not isinstance(content, str):
                raise ValueError("Web Script Index did not return an HTML/text page")
            ops = parse_webscript_index(content)
            if ops:
                return ops
            errors.append(f"{path}: no templates found")
        except (PermissionError, RuntimeError, ValueError) as exc:
            errors.append(f"{path}: {type(exc).__name__}")
    # Make absence explicit in the registry warnings. No fallback to stale
    # cached endpoints or guessing methods from common URL patterns.
    raise RuntimeError("Web Script index unavailable/incomplete: " + "; ".join(errors))


registry.register_provider("webscript-index", discover_webscripts)
