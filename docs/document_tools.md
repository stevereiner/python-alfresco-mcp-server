# Independent document tools

These feature modules augment the existing MCP tools; they do not change or
replace the runtime API registry, Web Script discovery, actions, identity
handling, or existing tool-contract fixes. The normal server entry point
registers the modules present in the installation. Missing optional feature
modules are skipped; missing dependencies inside an installed module are not.

The five independent modules are `document_text`, `remote_content`,
`custom_metadata`, `node_relocation`, and `folder_pagination`. Each feature
branch adds only its own implementation, tests and guide. The HTTP helper,
registration loader and their tests are identical across the five branches,
so they can be merged once without introducing feature dependencies.

## Identity and transport

All requests reuse `get_core_client()` and its authenticated HTTP client.
No tool accepts a remote host, password, ticket, or bearer token. Permission
checks remain the responsibility of Alfresco and the configured identity.
This does NOT add per-user authentication to the legacy connection layer;
integrate and validate the separate identity feature for multi-user use.

Use HTTPS with `ALFRESCO_VERIFY_SSL=true`. These features do not modify the
legacy TLS defaults or authenticate the MCP HTTP listener. Redirects are not
followed by the new document HTTP helper, to avoid credential redirection.
Network errors are sanitized and mutations are never automatically retried.
After a timeout, inspect repository state before retrying a write.

## Explicit write opt-in

New write tools require `MCP_DOCUMENT_WRITES_ENABLED=true` (default: false).
This gate is NOT a global read-only mode: it does not disable legacy write
tools or other extensions. Remove/disable legacy tools and restrict the
Alfresco account separately where a read-only service is required. MCP
annotations communicate tool effects but are not authorization controls or
human approval. Do not give the AI an administrator account.

## Limits

`MCP_DOCUMENT_MAX_BYTES` defaults to 10485760 (10 MiB), with a hard ceiling
of 16777216 (16 MiB). The effective limit is the smaller of this value and
`MAX_FILE_SIZE` (default 100000000). Invalid/zero limits fail closed.
JSON responses are limited to 2 MiB, including streamed responses without a
Content-Length. These limits apply only to the new tools. Inline Base64
transfers are for small files, not a large-document transfer protocol.

## Validation

Run the focused, offline unit tests in an installed development environment:

```bash
python -m unittest discover -s tests/document_features -v
```

They mock Alfresco HTTP responses and check argument validation, bounded
reads, errors, the write gate, and registration. They are not a replacement
for the project's full suite or a live Alfresco/MCP/Keycloak integration test.
No workflows, identity-provider configuration, or repository data are changed
by these tests.
