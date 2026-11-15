import base64
import os
import unittest
from unittest.mock import AsyncMock, patch
from alfresco_mcp_server.tools.core import remote_content as m


class RemoteContentTests(unittest.IsolatedAsyncioTestCase):
    async def test_upload_uses_explicit_filename_and_no_disk(self):
        with patch.dict(os.environ, {'MCP_DOCUMENT_WRITES_ENABLED': 'true'}), \
             patch.object(m, 'request_json', AsyncMock(return_value={'entry': {'id': 'new'}})) as req:
            await m.upload_document_content('report.txt', text_content='Città', description='Test')
        self.assertEqual(req.call_args.args, ('POST', '/nodes/-shared-/children'))
        self.assertEqual(req.call_args.kwargs['files']['filedata'], ('report.txt', 'Città'.encode(), 'text/plain'))
        self.assertEqual(req.call_args.kwargs['data']['cm:title'], 'report.txt')
        self.assertEqual(req.call_args.kwargs['data']['autoRename'], 'false')

    async def test_binary_and_empty_payloads(self):
        self.assertEqual(m.decode_content(base64.b64encode(b'\x00\xff').decode(), None), b'\x00\xff')
        self.assertEqual(m.decode_content('', None), b'')
        self.assertEqual(m.decode_content(None, ''), b'')

    async def test_invalid_content(self):
        for args in ((None, None), ('', ''), ('***', None), ('YWJj\n', None), ('é', None)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                m.decode_content(*args)

    async def test_byte_limits_not_character_limits(self):
        with patch.dict(os.environ, {'MCP_DOCUMENT_MAX_BYTES': '3'}):
            with self.assertRaises(ValueError):
                m.decode_content(None, 'éé')
            with self.assertRaises(ValueError):
                m.decode_content(base64.b64encode(b'abcd').decode(), None)

    async def test_update_content_and_version_flags(self):
        with patch.dict(os.environ, {'MCP_DOCUMENT_WRITES_ENABLED': 'true'}), \
             patch.object(m, 'request_json', AsyncMock(return_value={'entry': {'id': 'node'}})) as req:
            await m.update_document_content('node', text_content='changed', major_version=True, comment='Revision')
        self.assertEqual(req.call_args.args, ('PUT', '/nodes/node/content'))
        self.assertEqual(req.call_args.kwargs['params'], {'majorVersion': 'true', 'comment': 'Revision'})
        self.assertEqual(req.call_args.kwargs['content'], b'changed')

    async def test_name_and_mime_validation(self):
        with patch.dict(os.environ, {'MCP_DOCUMENT_WRITES_ENABLED': 'true'}):
            for kwargs in ({'filename': '../file', 'text_content': 'x'},
                           {'filename': 'a', 'text_content': 'x', 'mime_type': 'text/plain\r\nSecret: x'}):
                with self.assertRaises(ValueError), patch.object(m, 'request_json', AsyncMock()) as req:
                    await m.upload_document_content(**kwargs)
                req.assert_not_awaited()

    async def test_disabled_writes(self):
        with patch.dict(os.environ, {'MCP_DOCUMENT_WRITES_ENABLED': 'false'}), \
             patch.object(m, 'request_json', AsyncMock()) as req:
            with self.assertRaises(PermissionError):
                await m.upload_document_content('a', text_content='x')
        req.assert_not_awaited()
