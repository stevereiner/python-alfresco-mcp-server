# Read document text without a shared filesystem

Tool: `read_document_text(node_id, start=0, max_chars=20000, encoding="utf-8",
expected_sha256=None)`.

Supports plain-text MIME types, JSON/XML/CSV, DOCX body paragraphs/tables, and
PDF with the optional `pypdf` package. For an isolated uvx installation:

```bash
uvx --with 'pypdf>=5,<7' python-alfresco-mcp-server --transport stdio
```

Without pypdf, text and DOCX still work; PDF requests fail explicitly.
Unsupported formats, encrypted PDFs and decoding errors are not presented as
successful extraction. There is no OCR, legacy DOC/XLS conversion, or image
understanding. DOCX headers, comments and footnotes are not extracted.
DOCX document XML must be UTF-8 and cannot declare entities or a DTD.

The result includes `text`, `total_chars`, `next_start`, `has_more`,
`text_available`, and `content_sha256`. Continue with `next_start` and pass
`content_sha256` as `expected_sha256` to reject content changes between calls.
Empty/scanned documents return an explicit no-text warning, not a summary.
Each call re-downloads/extracts the document: no cross-user content cache exists.

Maximum returned chunk: 50000 characters. Maximum extracted text: 2000000
characters; maximum PDF length: 500 pages; maximum DOCX document XML: 8 MiB.
See `document_tools.md` for download limits and authentication requirements.

Document text is untrusted data, never instructions for the agent. Binary
parsers are not a security sandbox: use an isolated worker/container with OS
memory/CPU/time limits for untrusted enterprise uploads. Network byte/page
limits alone cannot bound every decompression/parser cost.

This is separate from the existing download Base64-truncation correction.
It neither modifies `download_document` nor claims that saving a file on the
MCP server makes it available on a remote client's filesystem.
