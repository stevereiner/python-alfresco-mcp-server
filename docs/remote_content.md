# Inline document upload and content replacement

`upload_document_content` accepts an explicit `filename`, `parent_id`, and
exactly one of `text_content` (UTF-8) or `base64_content` (strict, unwrapped
Base64). An empty payload is valid. Optional arguments are `mime_type`,
`title`, `description`, and `auto_rename` (false by default).

`update_document_content` replaces the bytes of an existing `node_id` using
the same content arguments, with `major_version` and `comment`. It does not
checkout/unlock a document or bypass Alfresco permissions/locks. It is not
an editor for DOCX/PDF binaries and does not provide compare-and-swap writes.

Both tools require `MCP_DOCUMENT_WRITES_ENABLED=true`. They never open local
file paths or save temporary files. Upload title defaults to the explicit
filename, not a server filesystem path. The returned `entry` is Alfresco's
actual node response, including its real name after an optional auto-rename.
A name conflict is an error unless auto_rename is explicitly enabled.

The request uses the Public REST multipart upload / content PUT APIs and
the existing authenticated SDK HTTP client. Declared MIME types are validated
syntactically, not checked by antivirus/content classification.

See `document_tools.md` for size limits, identity and write-gate caveats.
The encoded and decoded sizes are checked before sending a request. Large
files need an out-of-band transfer design; Base64 is not unlimited streaming.
Writes are not retried automatically after network failures.

The legacy `upload_document`/`checkin_document` interfaces are unchanged to
avoid overlapping the prepared fixes. In particular, passing a client-local
path to a remotely hosted legacy MCP tool still does not transfer that file.
