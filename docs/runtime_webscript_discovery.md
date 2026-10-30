# Runtime Web Script discovery

This provider reads the **live Alfresco Web Script Index** rather than
loading OpenAPI/YAML/JSON catalogs from disk.

It tries `/alfresco/service/index/all` and `/alfresco/service/index`
through the server's existing authenticated Alfresco HTTP client. The index
must be accessible to the configured identity. No scripts are executed
during discovery.

## Limits of runtime introspection

The Web Script Index usually exposes a URI template and HTTP method, but
not necessarily a complete, machine-readable contract for required JSON
body/query parameters. This provider therefore defaults every indexed
operation to **discovered but non-executable**. Developers must not
interpret a discoverable path as proof that parameters have been understood.

For a controlled, read-only deployment,
`ALFRESCO_DISCOVERY_ALLOW_UNDESCRIBED_READS=true` permits discovered GETs
with the known URI path arguments. The flag is **off by default** and may
result in 4xx responses when a GET has required query parameters not
advertised by the index.

POST/PUT/PATCH/DELETE remain disabled until an authenticated runtime
metadata resolver supplies their full parameter contract and authorization
policy. A method/route listing alone is insufficient.

This module depends on `feature/alfresco-api-registry`; integrate that
foundation before merging this provider.

## Known limitations

- Index HTML can differ between Alfresco Community versions.
- Some deployments disable/admin-protect the Web Script Index.
- A list of Web Scripts is not automatically a list of every Alfresco Public
  REST endpoint.
- Neither `OPTIONS` nor an index page guarantees full JSON body schemas.
- Live plugin introspection may need a purpose-built Alfresco extension
  exposing descriptors for the installed Java/JavaScript implementation.
- Parsing is intentionally bounded; large/unsupported indexes fail closed.
