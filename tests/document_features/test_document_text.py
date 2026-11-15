import hashlib
from io import BytesIO
import unittest
from unittest.mock import AsyncMock, patch
import zipfile
from alfresco_mcp_server.tools.core import document_text as m


def docx(xml):
    data = BytesIO()
    with zipfile.ZipFile(data, 'w') as archive:
        archive.writestr('word/document.xml', xml)
    return data.getvalue()


class DocumentTextTests(unittest.IsolatedAsyncioTestCase):
    async def test_text_encoding(self):
        self.assertEqual(m.extract_text('Città'.encode(), 'text/plain', 'utf-8'), 'Città')
        self.assertEqual(m.extract_text(b'caf\xe9', 'text/plain', 'cp1252'), 'café')
        with self.assertRaises(ValueError):
            m.extract_text(b'caf\xe9', 'text/plain', 'utf-8')

    async def test_docx_paragraphs(self):
        xml = '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Hello</w:t><w:tab/><w:t>world</w:t></w:r></w:p><w:p><w:r><w:t>Next</w:t></w:r></w:p></w:body></w:document>'
        self.assertEqual(m.extract_text(docx(xml), m._DOCX, 'utf-8'), 'Hello\tworld\nNext')

    async def test_docx_entity_rejection(self):
        xml = '<!DOCTYPE doc [<!ENTITY x "evil">]><doc>&x;</doc>'
        for data in (xml.encode(), xml.encode('utf-16')):
            with self.assertRaises(ValueError):
                m.extract_text(docx(data), m._DOCX, 'utf-8')

    async def test_invalid_docx_and_unsupported_format(self):
        for content, mime in ((b'not zip', m._DOCX), (b'abc', 'application/msword'), (b'abc', 'image/png')):
            with self.assertRaises(ValueError):
                m.extract_text(content, mime, 'utf-8')

    async def test_chunking_and_digest(self):
        info = {'entry': {'isFile': True, 'name': 'doc.txt', 'content': {'mimeType': 'text/plain', 'sizeInBytes': 6}}}
        with patch.object(m, 'request_json', AsyncMock(return_value=info)), \
             patch.object(m, 'request_bytes', AsyncMock(return_value=b'abcdef')):
            first = await m.read_document_text('node', max_chars=3)
            second = await m.read_document_text('node', start=first['next_start'], max_chars=3,
                                                expected_sha256=first['content_sha256'])
        self.assertEqual(first['text'], 'abc')
        self.assertTrue(first['has_more'])
        self.assertEqual(second['text'], 'def')
        self.assertIsNone(second['next_start'])
        self.assertEqual(first['content_sha256'], hashlib.sha256(b'abcdef').hexdigest())

    async def test_changed_document(self):
        with patch.object(m, 'request_json', AsyncMock(return_value={'entry': {'isFile': True, 'content': {'mimeType': 'text/plain'}}})), \
             patch.object(m, 'request_bytes', AsyncMock(return_value=b'new')):
            with self.assertRaisesRegex(ValueError, 'changed'):
                await m.read_document_text('node', expected_sha256='old')

    async def test_reject_folder_and_oversized_document_before_download(self):
        for info in ({'isFile': False}, {'isFile': True, 'content': {'sizeInBytes': 999999999}}):
            with patch.object(m, 'request_json', AsyncMock(return_value={'entry': info})), \
                 patch.object(m, 'request_bytes', AsyncMock()) as req:
                with self.assertRaises(ValueError):
                    await m.read_document_text('node')
                req.assert_not_awaited()

    async def test_blank_document_is_explicit(self):
        with patch.object(m, 'request_json', AsyncMock(return_value={'entry': {'isFile': True, 'content': {'mimeType': 'text/plain'}}})), \
             patch.object(m, 'request_bytes', AsyncMock(return_value=b'')):
            result = await m.read_document_text('node')
        self.assertFalse(result['text_available'])
        self.assertTrue(result['warnings'])

    async def test_invalid_ranges(self):
        for kwargs in ({'start': -1}, {'max_chars': 0}, {'max_chars': 50001}):
            with self.assertRaises(ValueError), patch.object(m, 'request_json', AsyncMock()) as req:
                await m.read_document_text('node', **kwargs)
            req.assert_not_awaited()

    async def test_optional_pdf_parser(self):
        try:
            from pypdf import PdfWriter
        except ImportError:
            self.skipTest('pypdf optional dependency is not installed')
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        data = BytesIO()
        writer.write(data)
        self.assertEqual(m.extract_text(data.getvalue(), 'application/pdf', 'utf-8'), '')
        writer.encrypt('password')
        data = BytesIO()
        writer.write(data)
        with self.assertRaisesRegex(ValueError, 'Encrypted'):
            m.extract_text(data.getvalue(), 'application/pdf', 'utf-8')
