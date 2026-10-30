"""Discover Alfresco repository actions and declared parameters at runtime.

Requires the runtime registry/transport feature branch to be integrated first.
Supports the Public REST Actions API when the installed Alfresco version
actually exposes it. No static action catalog is required.
"""
from __future__ import annotations

import logging
import os
import re
from dataclasses import asdict, dataclass

from .registry import Operation, registry
from .transport import alfresco_request

logger = logging.getLogger(__name__)
_BASE = "/alfresco/api/-default-/public/alfresco/versions/1"
_DEFINITIONS = _BASE + "/action-definitions"
_EXECUTIONS = _BASE + "/action-executions"
_NAME = re.compile(r"^[A-Za-z0-9_.:-]+$")


@dataclass(frozen=True)
class ActionParameter:
    name: str
    kind: str
    mandatory: bool
    multiple: bool = False
    allowed_values: tuple = ()


@dataclass(frozen=True)
class ActionDefinition:
    id: str
    title: str
    description: str
    parameters: tuple[ActionParameter, ...]
    complete: bool


_definitions: dict[str, ActionDefinition] = {}


def _kind(value: str) -> str | None:
    value = str(value).lower()
    if value in ("d:text", "d:noderef", "d:qname", "d:date", "string", "text"):
        return "string"
    if value in ("d:int", "d:long", "integer", "int"):
        return "integer"
    if value in ("d:float", "d:double", "number", "float"):
        return "number"
    if value in ("d:boolean", "boolean", "bool"):
        return "boolean"
    return None


def _to_bool(value: object) -> bool:
    return value is True or str(value).lower() == "true"


def parse_action_definitions(payload: object) -> list[ActionDefinition]:
    """Accept the common REST list/entries/entry envelope; fail closed."""
    if isinstance(payload, dict):
        if isinstance(payload.get("list"), dict):
            payload = payload["list"].get("entries", [])
        elif isinstance(payload.get("entries"), list):
            payload = payload["entries"]
        else:
            payload = payload.get("actions", [])
    if not isinstance(payload, list):
        raise ValueError("Unsupported action-definition response")
    result = []
    for raw in payload[:250]:
        entry = raw.get("entry", raw) if isinstance(raw, dict) else {}
        if not isinstance(entry, dict):
            continue
        action_id = entry.get("id") or entry.get("actionDefinitionId")
        if not isinstance(action_id, str) or not _NAME.fullmatch(action_id):
            continue
        declared = entry.get("parameterDefinitions", entry.get("parameter_definitions"))
        # An absent definition list is NOT proof that an action needs no args.
        complete = isinstance(declared, list)
        params = []
        for raw_param in declared if isinstance(declared, list) else []:
            if not isinstance(raw_param, dict):
                complete = False
                continue
            name = raw_param.get("name")
            kind = _kind(raw_param.get("type", ""))
            if not isinstance(name, str) or not _NAME.fullmatch(name) or kind is None:
                complete = False
                continue
            allowed = raw_param.get("allowedValues", [])
            if not isinstance(allowed, list):
                allowed = []
            params.append(ActionParameter(
                name=name,
                kind=kind,
                mandatory=_to_bool(raw_param.get("mandatory", False)),
                multiple=_to_bool(raw_param.get("multiValued", False)),
                allowed_values=tuple(allowed),
            ))
        result.append(ActionDefinition(
            id=action_id,
            title=str(entry.get("name", action_id)),
            description=str(entry.get("description", "")),
            parameters=tuple(params),
            complete=complete,
        ))
    return result


async def discover_actions() -> list[Operation]:
    global _definitions
    # Query the running installation; a disabled API must not leave cached
    # action descriptions/execution permissions active.
    _definitions = {}
    result = await alfresco_request("GET", _DEFINITIONS)
    discovered = parse_action_definitions(result["data"])
    _definitions = {item.id: item for item in discovered}
    return [
        Operation(
            id="action:runtime." + item.id.lower(),
            method="POST",
            path=_EXECUTIONS,
            source="action-definitions",
            description=item.description or item.title,
            executable=False,  # generic executor never bypasses action validation
            effect="mutate",
            metadata={
                "action_id": item.id,
                "parameter_contract_complete": str(item.complete).lower(),
            },
        )
        for item in discovered
    ]


async def list_actions() -> list[dict]:
    await registry.ensure_fresh()
    return [asdict(d) for d in sorted(_definitions.values(), key=lambda a: a.id)]


async def describe_action(action_id: str) -> dict:
    await registry.ensure_fresh()
    if action_id not in _definitions:
        raise ValueError(f"Action not found in runtime definitions: {action_id}")
    return asdict(_definitions[action_id])


def _check_action_parameters(definition: ActionDefinition, params: dict) -> None:
    if not definition.complete:
        raise PermissionError("Action parameter contract is incomplete")
    if not isinstance(params, dict):
        raise ValueError("Action parameters must be an object")
    known = {param.name: param for param in definition.parameters}
    for key in params:
        if key not in known:
            raise ValueError(f"Undeclared action parameter: {key}")
    for param in definition.parameters:
        if param.mandatory and (param.name not in params or params[param.name] is None):
            raise ValueError(f"Required action parameter missing: {param.name}")
        if param.name not in params or params[param.name] is None:
            continue
        values = params[param.name] if param.multiple else [params[param.name]]
        if not isinstance(values, list):
            raise ValueError(f"Expected an array for {param.name}")
        for value in values:
            if param.kind == "string" and type(value) is not str:
                raise ValueError(f"Expected string for {param.name}")
            if param.kind == "integer" and type(value) is not int:
                raise ValueError(f"Expected integer for {param.name}")
            if param.kind == "number" and type(value) not in (int, float):
                raise ValueError(f"Expected number for {param.name}")
            if param.kind == "boolean" and type(value) is not bool:
                raise ValueError(f"Expected boolean for {param.name}")
            if param.allowed_values and value not in param.allowed_values:
                raise ValueError(f"Not an allowed value for {param.name}")


async def execute_action(action_id: str, node_id: str, parameters: dict) -> dict:
    await registry.ensure_fresh()
    if action_id not in _definitions:
        raise ValueError("Unknown action definition")
    if action_id not in {
        x.strip() for x in os.getenv("ALFRESCO_ALLOWED_ACTIONS", "").split(",")
        if x.strip()
    }:
        raise PermissionError("Action is not explicitly allowed by the administrator")
    if not isinstance(node_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", node_id):
        raise ValueError("Invalid action target ID")
    definition = _definitions[action_id]
    _check_action_parameters(definition, parameters)
    return await alfresco_request(
        "POST",
        _EXECUTIONS,
        body={"actionDefinitionId": action_id, "targetId": node_id, "params": parameters},
    )


registry.register_provider("action-definitions", discover_actions)
