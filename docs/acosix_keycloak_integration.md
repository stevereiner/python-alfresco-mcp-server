# Acosix Alfresco Keycloak integration

This feature preserves the existing OAuth2 bearer implementation in
`python-alfresco-api` and adds an **opt-in** validated-caller-token mode
for the Acosix repository authentication subsystem.

## What is special about Acosix?

[Acosix alfresco-keycloak](https://github.com/Acosix/alfresco-keycloak)
implements its own Repository authentication subsystem and is distinct from
the built-in `identity-service`. It can accept a client-obtained Keycloak
Bearer token for a repository user. The Acosix addon maps token identities
and roles to Alfresco users/authorities. Final ACL checks remain Alfresco's
responsibility.

Example server-side `alfresco-global.properties` (illustrative only):

```properties
authentication.chain=alfrescoNtlm1:alfrescoNtlm,keycloak1:keycloak
keycloak.adapter.realm=alfresco
keycloak.adapter.resource=alfresco
# plus correct auth-server-url and credentials in secure config
```

The token's audience, realm and user mapping **must** be accepted by the
installed Acosix adapter. Acosix `sso.handlePublicApi=false` controls
browser SSO handling; do not assume it proves or disproves Bearer support
for all REST paths. Test the actual REST API and custom Web Script routes.

## Single service identity (existing behavior)

```env
ALFRESCO_AUTH_METHOD=oauth2
ALFRESCO_OAUTH2_ACCESS_TOKEN=<user-bearer>
```

This runs the server as one configured Alfresco identity. It is not a
multi-user delegated-authentication configuration.

## Per-user MCP caller token passthrough (new, explicit opt-in)

```env
ALFRESCO_AUTH_METHOD=oauth2
ALFRESCO_AUTH_USE_CALLER_TOKEN=true
MCP_TRANSPORT_AUTH=true
MCP_AUTH_JWKS_URI=https://keycloak.example/realms/alfresco/protocol/openid-connect/certs
MCP_AUTH_ISSUER=https://keycloak.example/realms/alfresco
MCP_AUTH_AUDIENCE=alfresco-mcp
ALFRESCO_VERIFY_SSL=true
```

FastMCP validates the incoming bearer before the server accesses it. The
backend client is created in task-local context and cannot be reused across
different validated bearer identities. User-token mode does not receive
service-account secrets or a service refresh token: expiry fails closed.

**Important**: The token has to be acceptable to **both** MCP JWT
validation and the Alfresco repository's Acosix audience checks. A token
issued solely for the `alfresco-mcp` audience may be rejected by Acosix
if `alfresco` is not an accepted audience. Configure legitimate audience
mapping in Keycloak, or implement an audited RFC 8693 token-exchange flow.
Do not disable token audience verification merely to make it work.

This implementation does **not** provide an Authorization Code UI, token
exchange, unattended refresh of a user's token, or automatic login
redirect handling. Those would be separate explicit integrations.
`stdio` transport has no authenticated HTTP caller; in that mode use a
configured Alfresco identity instead of caller passthrough.

## Security checks before production

- Verify RS256 JWT signatures, HTTPS issuer and intended MCP audience.
- Confirm Keycloak user tokens are accepted at both the REST API and
  `/alfresco/service/` Web Scripts when the Acosix addon is installed.
- Confirm 401/403 responses for expired, wrong-audience and unprivileged
  tokens; do not fall back to an admin account.
- Verify two simultaneous user requests never share the same Alfresco
  client or access token.
- Enable HTTPS certificate validation in production.
- Ensure operation catalogs/introspection endpoints do not leak privileged
  metadata across different users. For production multi-user deployment,
  prefer a curated common discovery identity for catalog publication or
  identity-scoped catalog caches.

Compatibility must be checked with the deployed Alfresco, Acosix and
Keycloak releases; these offline tests do not assert live compatibility.
