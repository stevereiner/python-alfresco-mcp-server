"""Offline Action Definition parsing and parameter contract tests."""
import pytest

# This provider is a targeted follow-up to the runtime Registry branch.
pytest.importorskip("alfresco_mcp_server.discovery.registry")

from alfresco_mcp_server.discovery.actions import (
    parse_action_definitions, _check_action_parameters,
)


DEFINITIONS = {
    "list": {"entries": [{"entry": {
        "id": "custom-process",
        "name": "Custom process",
        "parameterDefinitions": [
            {"name": "force", "type": "d:boolean", "mandatory": True},
            {"name": "mode", "type": "d:text", "allowedValues": ["fast", "safe"]},
            {"name": "targets", "type": "d:noderef", "multiValued": True},
        ],
    }}]}
}


def test_runtime_definitions_are_typed():
    items = parse_action_definitions(DEFINITIONS)
    assert len(items) == 1
    action = items[0]
    assert action.complete
    assert len(action.parameters) == 3
    _check_action_parameters(
        action, {"force": True, "mode": "fast", "targets": ["node-1"]}
    )


def test_missing_required_action_parameter_rejected():
    action = parse_action_definitions(DEFINITIONS)[0]
    with pytest.raises(ValueError, match="Required"):
        _check_action_parameters(action, {"mode": "fast"})


def test_wrong_type_and_enum_rejected():
    action = parse_action_definitions(DEFINITIONS)[0]
    with pytest.raises(ValueError, match="boolean"):
        _check_action_parameters(action, {"force": "true"})
    with pytest.raises(ValueError, match="allowed value"):
        _check_action_parameters(action, {"force": True, "mode": "unknown"})


def test_undefined_contract_is_not_executable():
    item = parse_action_definitions([{"id": "unknown-action"}])[0]
    assert not item.complete
    with pytest.raises(PermissionError):
        _check_action_parameters(item, {})


def test_unknown_parameter_rejected():
    action = parse_action_definitions(DEFINITIONS)[0]
    with pytest.raises(ValueError, match="Undeclared"):
        _check_action_parameters(action, {"force": True, "notDeclared": 42})
