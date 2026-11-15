# Structured folder pagination

`browse_repository_page(parent_id="-my-", skip_count=0, max_items=25,
order_by="name ASC")` returns exactly one folder page.

The response preserves `entries` and Alfresco's `pagination` object, plus
`next_skip_count`. Follow that offset until it is null. Offsets come from
the actual response count, not the requested page size. Missing/inconsistent
pagination metadata is an error, not evidence that a listing is complete.

Allowed page size: 1-1000. Sorting: name, createdAt or modifiedAt followed by
ASC/DESC. Names are used by default for predictable ordering. Concurrent
repository changes can still alter subsequent pages; this is not an atomic
snapshot or a recursive export. There is no search-results pagination in
this feature, and no claim that one page contains all documents.

The legacy `browse_repository` is unchanged. The new tool is read-only and
uses the existing authenticated identity. See `document_tools.md` for limits
and focused tests.
