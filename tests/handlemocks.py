import unittest

from httmock import response, urlmatch


class HandleMocks(object):
    VIEW_HANDLE_RESPONSE = (
        """{"responseCode":1,"handle":"21.T99999/test-handle","values":[{"index":1,"type":"URL","data":"""
        """{"format":"string","value":"https://www.example.com"},"ttl":86400,"timestamp":"2026-01-07T18:47:40Z"}"""
        """,{"index":2,"type":"title","data":{"format":"string","value":"TEST"},"ttl":86400,"timestamp":"""
        """"2026-01-07T18:47:40Z"},{"index":3,"type":"description","data":{"format":"string","value":"A test handle"}"""
        ""","ttl":86400,"timestamp":"2026-01-07T18:47:40Z"},{"index":100,"type":"HS_ADMIN","data":"""
        """{"format":"admin","value":{"handle":"21.T99999/TESTUSER01","index":301,"permissions":"011111110011"}},"""
        """"ttl":86400,"timestamp":"2026-01-07T18:47:40Z"}]}"""
    )

    view_handle_urlmatch = dict(
        netloc="localhost", path="/api/handles/21.T99999/test-handle", method="GET"
    )

    @urlmatch(**view_handle_urlmatch)
    def view_handle_mock(self, url, request):
        assert url.path == "/api/handles/21.T99999/test-handle"
        assert request.method == "GET"
        return response(200, self.VIEW_HANDLE_RESPONSE, None, None, 5, request)


class TestHandlesBase(unittest.TestCase):
    def _validateHandle(self, handle):
        self.assertIsNotNone(handle)
        self.assertEqual(handle.id, "test-handle")
        self.assertIsNotNone(handle.values)
        self.assertEqual(len(handle.values), 5)
        self.assertEqual(handle.values["URL"].index, 1)
        self.assertEqual(handle.values["URL"].data_type, "string")
        self.assertEqual(handle.values["URL"].ttl, 86400)
        self.assertEqual(handle.values["URL"].timestamp, "2026-01-07T18:47:40Z")
        self.assertEqual(handle.values["URL"].data, "https://www.example.com")
        self.assertEqual(handle.values["title"].index, 2)
        self.assertEqual(handle.values["title"].data_type, "string")
        self.assertEqual(handle.values["title"].ttl, 86400)
        self.assertEqual(handle.values["title"].timestamp, "2026-01-07T18:47:40Z")
        self.assertEqual(handle.values["title"].data, "TEST")
        self.assertEqual(handle.values["description"].index, 3)
        self.assertEqual(handle.values["description"].data_type, "string")
        self.assertEqual(handle.values["description"].ttl, 86400)
        self.assertEqual(handle.values["description"].timestamp, "2026-01-07T18:47:40Z")
        self.assertEqual(handle.values["description"].data, "A test handle")
        self.assertEqual(handle.values["HS_ADMIN"].index, 100)
        self.assertEqual(handle.values["HS_ADMIN"].data_type, "admin")
        self.assertEqual(handle.values["HS_ADMIN"].ttl, 86400)
        self.assertEqual(handle.values["HS_ADMIN"].timestamp, "2026-01-07T18:47:40Z")
        self.assertIsNotNone(handle.values["HS_ADMIN"].data)
        self.assertEqual(handle.values["HS_ADMIN"].data["handle"], '21.T99999/TESTUSER01')
        self.assertEqual(handle.values["HS_ADMIN"].data["index"], 301)
        self.assertEqual(handle.values["HS_ADMIN"].data["permissions"], '011111110011')
