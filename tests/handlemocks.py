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
