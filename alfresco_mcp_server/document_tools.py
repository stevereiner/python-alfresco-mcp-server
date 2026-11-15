"""Register only the independently installed document feature modules."""
from importlib import import_module

_MODULES = (
    "document_text",
    "remote_content",
    "custom_metadata",
    "node_relocation",
    "folder_pagination",
)


def register_document_tools(mcp) -> None:
    for feature in _MODULES:
        name = "alfresco_mcp_server.tools.core." + feature
        try:
            module = import_module(name)
        except ModuleNotFoundError as exc:
            if exc.name != name:
                raise  # A missing dependency is not an absent optional feature.
            continue
        module.register(mcp)
