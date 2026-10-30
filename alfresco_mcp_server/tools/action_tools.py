"""Action-specific MCP tools, using runtime definitions rather than fixed args."""
from ..discovery.actions import list_actions, describe_action, execute_action


async def list_alfresco_actions_impl() -> dict:
    return {"actions": await list_actions()}


async def describe_alfresco_action_impl(action_id: str) -> dict:
    return await describe_action(action_id)


async def execute_alfresco_action_impl(
    action_id: str, node_id: str, parameters: dict | None = None
) -> dict:
    return await execute_action(action_id, node_id, parameters or {})


def register_action_tools(mcp) -> None:
    """Register the optional MCP tools after the core Registry is installed."""

    @mcp.tool
    async def list_alfresco_actions() -> dict:
        """List action definitions currently advertised by Alfresco."""
        return await list_alfresco_actions_impl()

    @mcp.tool
    async def describe_alfresco_action(action_id: str) -> dict:
        """Inspect the typed contract of an installed Alfresco action."""
        return await describe_alfresco_action_impl(action_id)

    @mcp.tool
    async def execute_alfresco_action(
        action_id: str, node_id: str, parameters: dict | None = None
    ) -> dict:
        """Run a specifically allowlisted action with validated arguments."""
        return await execute_alfresco_action_impl(action_id, node_id, parameters)
