"""Small, side-effect-free path helpers for files originating in Alfresco.

The server must not trust node names when constructing local download paths.
"""
import re

_BAD_SEGMENT = re.compile(r'[<>:"|?*\x00-\x1f/\\\\]')


def safe_file_component(value: str, *, max_length: int = 180) -> str:
    """Return a single safe local file/directory component.

    Both POSIX and Windows separators are treated as untrusted input. The
    result cannot be an absolute path, '.' or '..'. A blank input is rejected.
    """
    if not isinstance(value, str) or not value:
        raise ValueError("Missing file name")
    name = _BAD_SEGMENT.sub("_", value).strip(" .")
    name = name[:max_length].rstrip(" .")
    if not name or name in (".", ".."):
        raise ValueError("Invalid file name")
    return name


def safe_node_id(value: str) -> str:
    """Normalize known node-ID forms while rejecting URL/path injection."""
    if not isinstance(value, str):
        raise ValueError("Node ID must be a string")
    node_id = value.strip()
    if node_id.startswith("alfresco://"):
        node_id = node_id.rsplit("/", 1)[-1]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", node_id):
        raise ValueError("Invalid Alfresco node ID")
    return node_id
