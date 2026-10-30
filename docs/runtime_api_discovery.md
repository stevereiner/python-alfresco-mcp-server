# Live Alfresco REST discovery

This implementation uses the running Alfresco instance as the source of
truth, **not** checked-in or downloaded static OpenAPI documents.

The REST bootstrap provider performs authenticated, safe GET probes against
a small set of known Alfresco Public REST entry paths (repository discovery,
current user, sites and root node). Only responding endpoints are published.
This is deliberately **not** an exhaustive list of REST endpoints: Alfresco
does not guarantee that a generic discover-all-REST-operations endpoint is
available. The Web Script Index adapter discovers additional registered
standard and custom Web Scripts when the deployment exposes the index.

The operation registry stores a bounded cache with
`ALFRESCO_DISCOVERY_TTL=300` (seconds), supports explicit refresh and
invalidates removed endpoints. Registered providers are evaluated again
against the configured Alfresco instance, and failed discovery never makes
a stale operation executable.

MCP tools:
- `list_alfresco_operations(query, source, refresh)`
- `describe_alfresco_operation(operation_id)`
- `invoke_alfresco_operation(operation_id, arguments)`
- `refresh_alfresco_discovery()`

Invocation only accepts a previously discovered, explicitly executable ID.
Paths stay on the configured Alfresco origin, typed parameters are validated,
redirects and unrecognized response types are not blindly followed. POST,
PATCH, PUT and DELETE require individual IDs in
`ALFRESCO_RUNTIME_ALLOWED_MUTATIONS`, even after a trusted provider
advertises an executable contract.

The server will never infer complete query or JSON body schemas from the
fact that an endpoint exists. Custom Web Scripts and Java Actions that
don't expose sufficient runtime metadata remain discoverable but not
generically executable until such metadata is available.

Deployment compatibility, reverse-proxy path prefixes and the actual
registered Web Script index structure require tests against a real instance.
