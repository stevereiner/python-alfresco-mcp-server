import unittest
from unittest.mock import AsyncMock, patch
from alfresco_mcp_server.tools.core import folder_pagination as m


def payload(offset=0, count=2, more=True):
    return {'list': {'entries': [{'entry': {'id': str(i)}} for i in range(count)],
                     'pagination': {'skipCount': offset, 'count': count, 'hasMoreItems': more}}}


class PaginationTests(unittest.IsolatedAsyncioTestCase):
    async def test_next_offset_and_forwarded_arguments(self):
        with patch.object(m, 'request_json', AsyncMock(return_value=payload(25))) as req:
            result = await m.browse_repository_page('folder', 25, 10, 'name DESC')
        self.assertEqual(result['next_skip_count'], 27)
        self.assertEqual(req.call_args.kwargs['params']['skipCount'], 25)
        self.assertEqual(req.call_args.kwargs['params']['maxItems'], 10)
        self.assertEqual(req.call_args.kwargs['params']['orderBy'], 'name DESC')

    async def test_empty_last_page(self):
        with patch.object(m, 'request_json', AsyncMock(return_value=payload(0, 0, False))):
            result = await m.browse_repository_page()
        self.assertIsNone(result['next_skip_count'])
        self.assertEqual(result['entries'], [])

    async def test_bad_inputs(self):
        for kwargs in ({'skip_count': -1}, {'skip_count': True}, {'max_items': 0},
                       {'max_items': 1001}, {'order_by': 'unknown'}, {'parent_id': '../bad'}):
            with self.subTest(kwargs=kwargs), patch.object(m, 'request_json', AsyncMock()) as req:
                with self.assertRaises(ValueError):
                    await m.browse_repository_page(**kwargs)
                req.assert_not_awaited()

    async def test_inconsistent_response(self):
        for result in ({}, {'list': {'entries': []}}, payload(0, 0, True),
                       {'list': {'entries': [], 'pagination': {'count': 1, 'skipCount': 0, 'hasMoreItems': False}}}):
            with patch.object(m, 'request_json', AsyncMock(return_value=result)), self.assertRaises(RuntimeError):
                await m.browse_repository_page()
