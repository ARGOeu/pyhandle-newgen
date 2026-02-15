import base64
import unittest
import urllib.parse

from httmock import response, urlmatch

from pymod import HandleServiceException


class HandleMocks(object):
    def _mock_auth(self, url, request):
        if not ("Authorization" in request.headers.keys() and "Basic {0}".format(
                base64.b64encode(
                    (
                        urllib.parse.quote_plus("301:21.T99999/TESTUSER01") + ":" + urllib.parse.quote_plus("s3cr3t")
                        ).encode("ascii")).decode("ascii")) == request.headers['Authorization']):
            raise HandleServiceException({
                "code": 403,
                "response_code": 403,
                "message": "Authentication Failure"
                },
                request=request.url,
            )

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
        self._mock_auth(url, request)
        return response(200, self.VIEW_HANDLE_RESPONSE, None, None, 5, request)

    DELETE_HANDLE_RESPONSE = (
        """{"responseCode":1,"handle":"21.T99999/test-handle"}"""
        )

    delete_handle_urlmatch = dict(
        netloc="localhost", path="/api/handles/21.T99999/test-handle", method="DELETE"
    )

    @urlmatch(**delete_handle_urlmatch)
    def delete_handle_mock(self, url, request):
        assert url.path == "/api/handles/21.T99999/test-handle"
        assert request.method == "DELETE"
        self._mock_auth(url, request)
        return response(200, self.DELETE_HANDLE_RESPONSE, None, None, 5, request)


class TestHandlesBase(unittest.TestCase):
    def _validateHandle(self, handle):
        self.assertIsNotNone(handle)
        self.assertEqual(handle.id, "test-handle")
        self.assertIsNotNone(handle.values)
        self.assertEqual(len(handle.values), 5)
        self.assertEqual(handle.values.by_name("URL")[0].index, 1)
        self.assertEqual(handle.values.by_name("URL")[0].data_type, "string")
        self.assertEqual(handle.values.by_name("URL")[0].ttl, 86400)
        self.assertEqual(handle.values.by_name("URL")[0].timestamp, "2026-01-07T18:47:40Z")
        self.assertEqual(handle.values.by_name("URL")[0].data, "https://www.example.com")
        self.assertEqual(handle.values.by_name("title")[0].index, 2)
        self.assertEqual(handle.values.by_name("title")[0].data_type, "string")
        self.assertEqual(handle.values.by_name("title")[0].ttl, 86400)
        self.assertEqual(handle.values.by_name("title")[0].timestamp, "2026-01-07T18:47:40Z")
        self.assertEqual(handle.values.by_name("title")[0].data, "TEST")
        self.assertEqual(handle.values.by_name("description")[0].index, 3)
        self.assertEqual(handle.values.by_name("description")[0].data_type, "string")
        self.assertEqual(handle.values.by_name("description")[0].ttl, 86400)
        self.assertEqual(handle.values.by_name("description")[0].timestamp, "2026-01-07T18:47:40Z")
        self.assertEqual(handle.values.by_name("description")[0].data, "A test handle")
        self.assertEqual(handle.values.by_name("HS_ADMIN")[0].index, 100)
        self.assertEqual(handle.values.by_name("HS_ADMIN")[0].data_type, "admin")
        self.assertEqual(handle.values.by_name("HS_ADMIN")[0].ttl, 86400)
        self.assertEqual(handle.values.by_name("HS_ADMIN")[0].timestamp, "2026-01-07T18:47:40Z")
        self.assertIsNotNone(handle.values.by_name("HS_ADMIN")[0].data)
        self.assertEqual(handle.values.by_name("HS_ADMIN")[0].data["handle"], '21.T99999/TESTUSER01')
        self.assertEqual(handle.values.by_name("HS_ADMIN")[0].data["index"], 301)
        self.assertEqual(handle.values.by_name("HS_ADMIN")[0].data["permissions"], '011111110011')
