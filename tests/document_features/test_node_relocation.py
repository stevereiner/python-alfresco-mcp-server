import os
import unittest
from unittest.mock import AsyncMock, patch
from alfresco_mcp_server.tools.core import node_relocation as m


class RelocationTests(unittest.IsolatedAsyncioTestCase):
    async def test_copy(self):
        with patch.dict(os.environ, {'MCP_DOCUMENT_WRITES_ENABLED': 'true'}), \
             patch.object(m, 'request_json', AsyncMock(return_value={'entry': {'id': 'new'}})) as req:
            result = await m.copy_node('source', 'target', 'Copy.pdf')
        req.assert_awaited_once_with('POST', '/nodes/source/copy', json={'targetParentId': 'target', 'name': 'Copy.pdf'})
        self.assertEqual(result['entry']['id'], 'new')

    async def test_move(self):
        with patch.dict(os.environ, {'MCP_DOCUMENT_WRITES_ENABLED': 'true'}), \
             patch.object(m, 'request_json', AsyncMock(return_value={'entry': {'id': 'source'}})) as req:
            await m.move_node('source', 'target')
        req.assert_awaited_once_with('POST', '/nodes/source/move', json={'targetParentId': 'target'})

    async def test_disabled_does_not_call_alfresco(self):
        with patch.dict(os.environ, {'MCP_DOCUMENT_WRITES_ENABLED': 'false'}), \
             patch.object(m, 'request_json', AsyncMock()) as req:
            with self.assertRaises(PermissionError):
                await m.copy_node('source', 'target')
        req.assert_not_awaited()

    async def test_invalid_input_does_not_call_alfresco(self):
        for args in (('../source', 'target', None), ('source', 'target', '../file.pdf')):
            with patch.object(m, 'request_json', AsyncMock()) as req:
                with self.assertRaises(ValueError):
                    await m.move_node(*args)
                req.assert_not_awaited()

    async def test_error_propagates_once(self):
        with patch.dict(os.environ, {'MCP_DOCUMENT_WRITES_ENABLED': 'true'}), \
             patch.object(m, 'request_json', AsyncMock(side_effect=RuntimeError('HTTP 409'))) as req:
            with self.assertRaises(RuntimeError):
                await m.copy_node('source', 'target')
        self.assertEqual(req.await_count, 1)
