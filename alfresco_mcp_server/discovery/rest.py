"""Probe known Alfresco REST entry paths on the running installation.

These are *safe bootstrap probes*, not an OpenAPI catalogue. Only routes
actually responding to authenticated requests become runtime operations.
Custom routes are discovered via the installed Web Script provider.
"""
from __future__ import annotations

from dataclasses import dataclass

from .registry import Operation, Parameter, registry
from .transport import alfresco_request

_BASE = "/alfresco/api/-default-/public/alfresco/versions/1"


@dataclass(frozen=True)
class _Probe:
    id: str
    probe_path: str
    template: str
    description: str
    parameters: tuple[Parameter, ...] = ()


# A small, curated, read-only set of entry paths to test. This is not an API
# schema and is not considered a complete list of available REST routes.
_PROBES = (
    _Probe(
        "rest:runtime.repository.discovery",
        _BASE + "/discovery",
        _BASE + "/discovery",
        "Current Alfresco repository version, edition and modules",
    ),
    _Probe(
        "rest:runtime.people.me",
        _BASE + "/people/-me-",
        _BASE + "/people/-me-",
        "Current authenticated Alfresco user",
    ),
    _Probe(
        "rest:runtime.sites.list",
        _BASE + "/sites",
        _BASE + "/sites",
        "Sites visible to the current Alfresco identity",
    ),
    _Probe(
        "rest:runtime.nodes.get",
        _BASE + "/nodes/-root-",
        _BASE + "/nodes/{nodeId}",
        "Get a repository node by ID",
        (Parameter("nodeId", location="path", required=True),),
    ),
)


async def discover_rest_capabilities() -> list[Operation]:
    discovered: list[Operation] = []
    for item in _PROBES:
        try:
            result = await alfresco_request("GET", item.probe_path)
        except (RuntimeError, PermissionError, ValueError):
            continue  # Not accessible or not provided by this Alfresco instance.
        if result.get("status") != 200:
            continue
        discovered.append(Operation(
            id=item.id,
            method="GET",
            path=item.template,
            source="rest-runtime-probe",
            description=item.description,
            parameters=item.parameters,
            executable=True,
            effect="read",
            metadata={
                "origin": "live-get-probe",
                "probed_path": item.probe_path,
                "note": "Only explicitly known parameter contracts are exposed",
            },
        ))
    return discovered


registry.register_provider("rest-runtime-probe", discover_rest_capabilities)
