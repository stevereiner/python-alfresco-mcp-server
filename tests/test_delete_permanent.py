"""The MCP deletion flag must reach the Alfresco client."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from alfresco_mcp_server.tools.core.delete_node import delete_node_impl


@pytest.mark.asyncio
@pytest.mark.parametrize("permanent", [False, True])
async def test_delete_forwards_permanent(permanent):
    core = MagicMock()
    core.nodes.get.return_value = SimpleNamespace(
        entry=SimpleNamespace(name="example.txt")
    )
    factory = MagicMock()
    factory.create_core_client.return_value = core

    with patch(
        "alfresco_mcp_server.tools.core.delete_node.ensure_connection",
        new_callable=AsyncMock,
    ), patch(
        "alfresco_mcp_server.utils.connection.get_client_factory",
        new_callable=AsyncMock,
        return_value=factory,
    ):
        response = await delete_node_impl("abc-123", permanent=permanent)

    core.nodes.delete.assert_called_once_with("abc-123", permanent=permanent)
    assert "Deletion Complete" in response
