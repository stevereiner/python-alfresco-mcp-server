# Runtime Alfresco Actions

This feature depends on the runtime API registry. It queries the **live**
Alfresco Repository API at
`/alfresco/api/-default-/public/alfresco/versions/1/action-definitions`.

It parses published action IDs and parameter definitions, including required
flags, simple data types, multi-valued arguments and any exposed enumerations.
Missing/unsupported definitions are **not** guessed and are not executable.

MCP tools:
- `list_alfresco_actions` lists available runtime definitions.
- `describe_alfresco_action(action_id)` returns the known typed contract.
- `execute_alfresco_action(action_id, node_id, parameters)` validates all
  supplied action parameters and POSTs to `/action-executions`.

To opt into specific mutating actions, set:

```env
ALFRESCO_ALLOWED_ACTIONS=custom-process,copy
```

This allowlist is empty by default; an authenticated Alfresco user must still
possess the corresponding repository permissions. The action execution path
is only valid when supported by the target Alfresco Community version.
Test this capability on the target instance before enabling mutations.

Not all Java custom actions expose full parameter definitions through the
REST endpoint. Those actions remain discoverable but not executable until
the installed plugin exposes sufficient **runtime** metadata. This module
never reads static OpenAPI/JSON/YAML action catalogs.
