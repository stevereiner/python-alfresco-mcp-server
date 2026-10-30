"""Validated, in-memory catalog of Alfresco operations discovered at runtime."""
from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from dataclasses import asdict, dataclass, field
from typing import Awaitable, Callable

logger = logging.getLogger(__name__)
_VALID_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE"})
_VALID_LOCATIONS = frozenset({"path", "query", "body"})
_VALID_KINDS = frozenset({"string", "integer", "number", "boolean", "array", "object"})
_VARIABLE = re.compile(r"\{([A-Za-z][A-Za-z0-9_-]*)\}")


@dataclass(frozen=True)
class Parameter:
    name: str
    location: str = "query"
    kind: str = "string"
    required: bool = False
    description: str = ""
    allowed_values: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", self.name):
            raise ValueError("Invalid parameter name")
        if self.location not in _VALID_LOCATIONS:
            raise ValueError("Invalid parameter location")
        if self.kind not in _VALID_KINDS:
            raise ValueError("Unsupported parameter type")


@dataclass(frozen=True)
class Operation:
    id: str
    method: str
    path: str
    source: str
    description: str = ""
    parameters: tuple[Parameter, ...] = ()
    # An endpoint can be discovered even when its full contract is unknown.
    executable: bool = False
    effect: str = "unknown"  # read, mutate, unknown
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9_.:-]{1,180}", self.id):
            raise ValueError("Invalid operation ID")
        if self.method not in _VALID_METHODS:
            raise ValueError("Unknown method")
        if self.effect not in ("read", "mutate", "unknown"):
            raise ValueError("Invalid effect")
        if (not self.path.startswith("/alfresco/") or self.path.startswith("//")
                or "\\" in self.path or "?" in self.path or "#" in self.path
                or any(s in (".", "..") for s in self.path.split("/"))
                or re.search(r"%(?:2e|2f|5c|00)", self.path, re.I)):
            raise ValueError("Operation must use a safe Alfresco-local path")
        placeholders = set(_VARIABLE.findall(self.path))
        path_params = {p.name for p in self.parameters if p.location == "path"}
        if placeholders != path_params:
            raise ValueError("All URI placeholders need explicit path parameters")
        keys = [(p.location, p.name) for p in self.parameters]
        if len(set(keys)) != len(keys):
            raise ValueError("Duplicate operation parameters")
        if self.executable and self.effect == "unknown":
            raise ValueError("Unknown-effect operations cannot be executable")

    def public_dict(self) -> dict:
        return asdict(self)


Provider = Callable[[], Awaitable[list[Operation]]]


class RuntimeRegistry:
    """Discoverers replace the entire catalog on refresh; failure is fail-closed."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = max(10, ttl_seconds)
        self._providers: dict[str, Provider] = {}
        self._operations: dict[str, Operation] = {}
        self._updated_at = 0.0
        self._warnings: list[str] = []
        self._lock = asyncio.Lock()

    def register_provider(self, name: str, provider: Provider) -> None:
        if not name or name in self._providers:
            raise ValueError(f"Duplicate/invalid discovery provider: {name}")
        self._providers[name] = provider
        self._updated_at = 0.0

    async def refresh(self) -> dict:
        async with self._lock:
            operations: dict[str, Operation] = {}
            warnings: list[str] = []
            for name, provider in self._providers.items():
                try:
                    found = await provider()
                    for op in found:
                        if not isinstance(op, Operation):
                            raise TypeError(f"Invalid operation returned by {name}")
                        if op.id in operations:
                            warnings.append(f"Duplicate operation ID: {op.id}")
                            operations.pop(op.id, None)
                            continue
                        operations[op.id] = op
                except Exception as exc:
                    logger.warning("Discovery provider %s failed: %s", name, exc)
                    warnings.append(f"{name}: discovery unavailable")
            # Do not keep potentially stale executable operations when a source
            # is unavailable after a refresh.
            self._operations = operations
            self._warnings = warnings
            self._updated_at = time.monotonic()
            return self.summary()

    async def ensure_fresh(self) -> None:
        if not self._updated_at or time.monotonic() - self._updated_at >= self.ttl_seconds:
            await self.refresh()

    def summary(self) -> dict:
        return {
            "operations": len(self._operations),
            "providers": list(self._providers),
            "warnings": self._warnings,
            "ttl_seconds": self.ttl_seconds,
        }

    async def list_operations(self, query: str = "", source: str = "") -> list[dict]:
        await self.ensure_fresh()
        term = query.strip().lower()
        results = [
            o.public_dict()
            for o in sorted(self._operations.values(), key=lambda item: item.id)
            if (not source or o.source == source)
            and (not term or term in (o.id + " " + o.description).lower())
        ]
        return results[:250]

    async def describe(self, operation_id: str) -> Operation:
        await self.ensure_fresh()
        try:
            return self._operations[operation_id]
        except KeyError:
            raise ValueError(f"Operation not discovered: {operation_id}") from None


def _registry_ttl() -> int:
    try:
        return int(os.getenv("ALFRESCO_DISCOVERY_TTL", "300"))
    except ValueError:
        return 300


registry = RuntimeRegistry(ttl_seconds=_registry_ttl())


def load_builtin_providers() -> None:
    """Load optional providers without requiring all feature branches at once."""
    import importlib

    for name in (
        "alfresco_mcp_server.discovery.rest",
        "alfresco_mcp_server.discovery.webscripts",
        "alfresco_mcp_server.discovery.actions",
    ):
        try:
            importlib.import_module(name)
        except ModuleNotFoundError as exc:
            if exc.name != name:
                raise


load_builtin_providers()
