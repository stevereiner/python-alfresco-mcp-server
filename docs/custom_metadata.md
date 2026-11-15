# Complete metadata and custom property updates

`get_node_metadata(node_id)` returns the complete REST node entry, including
custom properties, aspect names and path. It does not reduce the response to
cm:title/cm:description/cm:author.

`set_node_properties(node_id, properties)` sends only the supplied property
map, for example `{"acme:contractId": "C-123", "acme:labels": ["signed"]}`.
Namespace-qualified names, JSON scalar/list values, finite numbers, and a
1 MiB payload limit are validated. Empty strings and null are forwarded;
the installed Alfresco content model determines validity/removal semantics.
The model and any required aspects must already exist on the node.

Updates require `MCP_DOCUMENT_WRITES_ENABLED=true`. This tool does not
create models, replace aspect lists, change ACLs, or provide optimistic
concurrency control. Use it only for an explicitly requested update; reading
existing values first does not lock the node against concurrent changes.

The legacy `get_node_properties` and `update_node_properties` remain
unchanged. This feature is separate from API/action discovery. See
`document_tools.md` for identity, limits and tests.
