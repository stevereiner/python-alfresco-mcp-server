"""MCP-facing interface to the runtime operation catalog."""
from ..discovery.registry import registry
from ..discovery.transport import invoke_operation


async def list_alfresco_operations_impl(
    query: str = "", source: str = "", refresh: bool = False
) -> dict:
    if refresh:
        await registry.refresh()
    return {
        "catalog": registry.summary(),
        "operations": await registry.list_operations(query=query, source=source),
    }


async def describe_alfresco_operation_impl(operation_id: str) -> dict:
    op = await registry.describe(operation_id)
    return op.public_dict()


async def invoke_alfresco_operation_impl(operation_id: str, arguments: dict) -> dict:
    op = await registry.describe(operation_id)
    return await invoke_operation(op, arguments)


async def refresh_alfresco_discovery_impl() -> dict:
    return await registry.refresh()
