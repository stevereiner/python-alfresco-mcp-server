import asyncio
import json
import os
import unittest
from unittest.mock import AsyncMock, patch
import httpx
from alfresco_mcp_server.tools.core import _document_http as h


class DocumentHttpTests(unittest.TestCase):
    def test_api_roots_and_proxy_prefix(self):
        expected = 'https://example.test/proxy/alfresco/api/-default-/public/alfresco/versions/1'
        for suffix in ('', '/alfresco', '/alfresco/api', '/alfresco/api/-default-/public',
                       '/alfresco/api/-default-/public/alfresco/versions/1'):
            with self.subTest(suffix=suffix):
                self.assertEqual(h.api_root('https://example.test/proxy' + suffix), expected)

    def test_invalid_base_urls(self):
        for value in ('file:///tmp/repo', 'https://user:secret@example.test',
                      'https://example.test/?ticket=secret', 'https://example.test/#x'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                h.api_root(value)

    def test_node_ids(self):
        for value in ('abc-123', '-my-', '-shared-', '-root-'):
            self.assertEqual(h.node_id(value), value)
        for value in ('../x', 'x/y', 'x?y', 'x%2fy', '', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                h.node_id(value)

    def test_filename_validation(self):
        self.assertEqual(h.filename('Contratto finale.pdf'), 'Contratto finale.pdf')
        for value in ('../a', 'a/b', 'a\\b', '.', '..', '', 'a\n', 'a.', 'a ', 'a:b'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                h.filename(value)

    def test_write_gate(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(PermissionError):
            h.require_writes()
        with patch.dict(os.environ, {'MCP_DOCUMENT_WRITES_ENABLED': 'true'}):
            h.require_writes()

    def test_limits(self):
        with patch.dict(os.environ, {'MAX_FILE_SIZE': '500', 'MCP_DOCUMENT_MAX_BYTES': '1000'}):
            self.assertEqual(h.byte_limit(), 500)
        for value in ('invalid', '0', '-1', '999999999'):
            with patch.dict(os.environ, {'MCP_DOCUMENT_MAX_BYTES': value}), self.assertRaises(ValueError):
                h.byte_limit()

    def test_authenticated_json_request(self):
        requests = []
        def handler(request):
            requests.append(request)
            return httpx.Response(200, json={'entry': {'id': 'abc'}})
        with httpx.Client(transport=httpx.MockTransport(handler), headers={'Authorization': 'Bearer TEST'}) as client:
            data = h._request(client, 'https://example.test/core', 'GET', '/nodes/abc', 1000)
        self.assertEqual(json.loads(data)['entry']['id'], 'abc')
        self.assertEqual(requests[0].headers['Authorization'], 'Bearer TEST')
        self.assertEqual(str(requests[0].url), 'https://example.test/core/nodes/abc')

    def test_redirect_is_not_followed(self):
        calls = []
        def handler(request):
            calls.append(request)
            return httpx.Response(302, headers={'location': 'https://other.test/secret'})
        with httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True) as client:
            with self.assertRaisesRegex(RuntimeError, 'HTTP 302'):
                h._request(client, 'https://example.test', 'GET', '/nodes/abc', 100)
        self.assertEqual(len(calls), 1)

    def test_response_limit_with_and_without_content_length(self):
        class Stream(httpx.SyncByteStream):
            def __iter__(self):
                yield b'a' * 200
        for response in (lambda: httpx.Response(200, content=b'a' * 200),
                         lambda: httpx.Response(200, stream=Stream())):
            with httpx.Client(transport=httpx.MockTransport(lambda req: response())) as client:
                with self.assertRaises(ValueError):
                    h._request(client, 'https://example.test', 'GET', '/nodes/abc', 100)

    def test_error_does_not_leak_body(self):
        with httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(403, text='SECRET'))) as client:
            with self.assertRaises(RuntimeError) as error:
                h._request(client, 'https://example.test', 'GET', '/nodes/abc', 100)
        self.assertNotIn('SECRET', str(error.exception))

    def test_write_timeout_not_retried(self):
        calls = []
        def handler(request):
            calls.append(request)
            raise httpx.ReadTimeout('secret URL', request=request)
        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            with self.assertRaisesRegex(RuntimeError, 'verify repository state') as error:
                h._request(client, 'https://example.test', 'POST', '/nodes/a/copy', 100, json={})
        self.assertEqual(len(calls), 1)
        self.assertNotIn('secret URL', str(error.exception))

    def test_invalid_paths(self):
        for path in ('//evil.test', '/nodes/../a', '/nodes/a?x=1', '/nodes/a%2fb'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                h._request(None, 'https://example.test', 'GET', path, 100)

    def test_json_validation(self):
        for raw in (b'not json', b'[]'):
            with patch.object(h, 'request_bytes', AsyncMock(return_value=raw)), self.assertRaises(RuntimeError):
                asyncio.run(h.request_json('GET', '/nodes/abc'))

    def test_entry_validation(self):
        with self.assertRaises(RuntimeError):
            h.entry({'entry': []})
