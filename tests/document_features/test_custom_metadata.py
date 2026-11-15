import os
import unittest
from unittest.mock import AsyncMock, patch
from alfresco_mcp_server.tools.core import custom_metadata as m


class MetadataTests(unittest.IsolatedAsyncioTestCase):
    async def test_custom_values_are_preserved(self):
        props = {'my:contractId': '123', 'my:labels': ['one', 'two'], 'cm:title': '', 'my:optional': None}
        with patch.dict(os.environ, {'MCP_DOCUMENT_WRITES_ENABLED': 'true'}), \
             patch.object(m, 'request_json', AsyncMock(return_value={'entry': {'properties': props}})) as req:
            result = await m.set_node_properties('node', props)
        req.assert_awaited_once_with('PUT', '/nodes/node', json={'properties': props})
        self.assertEqual(result['entry']['properties'], props)

    async def test_read_returns_full_metadata(self):
        info = {'id': 'node', 'properties': {'my:custom': 12}, 'aspectNames': ['my:contract']}
        with patch.object(m, 'request_json', AsyncMock(return_value={'entry': info})):
            result = await m.get_node_metadata('node')
        self.assertEqual(result['entry'], info)

    async def test_invalid_properties(self):
        for props in ({}, {'invalid': 1}, {'cm:title': {}}, {'my:list': [[]]},
                      {'my:number': float('nan')}, {'my:number': float('inf')},
                      {'my:long': 'x' * (1024 * 1024)}):
            with self.subTest(props=str(props)[:80]), self.assertRaises(ValueError):
                m.validate_properties(props)

    async def test_write_gate(self):
        with patch.dict(os.environ, {'MCP_DOCUMENT_WRITES_ENABLED': 'false'}), \
             patch.object(m, 'request_json', AsyncMock()) as req:
            with self.assertRaises(PermissionError):
                await m.set_node_properties('node', {'cm:title': 'new'})
        req.assert_not_awaited()

    async def test_alfresco_error_is_not_a_success(self):
        with patch.dict(os.environ, {'MCP_DOCUMENT_WRITES_ENABLED': 'true'}), \
             patch.object(m, 'request_json', AsyncMock(side_effect=RuntimeError('HTTP 403'))):
            with self.assertRaises(RuntimeError):
                await m.set_node_properties('node', {'cm:title': 'new'})
