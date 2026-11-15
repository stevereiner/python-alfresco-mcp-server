# Native document copy and move

Tools: `copy_node(node_id, target_parent_id, name=None)` and
`move_node(node_id, target_parent_id, name=None)`.

Both call the corresponding Public REST `/nodes/{id}/copy` or `/move`
endpoint. They do not emulate a move by download/upload/delete or silently
rename a conflicting destination. The optional name is a filename, not a
path. Alfresco controls permissions, type restrictions, copy semantics and
conflicts; no unsupported promise about copying version history is made.

Both require `MCP_DOCUMENT_WRITES_ENABLED=true`; move is marked destructive
in its MCP annotations. Those annotations are not a substitute for human
approval or repository permissions. Network failures are not retried: a
copy/move may already have completed when the response is lost.

This exposes explicit document operations rather than assuming that generic
discovery or an available repository action covers them. No existing tool
or prepared feature branch is modified. See `document_tools.md`.
