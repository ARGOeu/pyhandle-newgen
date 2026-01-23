import json
import unittest

from httmock import HTTMock

from pymod import HandleClient

from .handlemocks import HandleMocks


class TestHandles(unittest.TestCase):
    def setUp(self):
        self.handle_client = HandleClient.instantiate_with_username_and_password(
                "localhost/api/handles/21.T99999",
                "21.T99999/TESTUSER01",
                "s3cr3t")
        self.HandleMocks = HandleMocks()

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

    def testViewHandle(self):
        with HTTMock(self.HandleMocks.view_handle_mock):
            handle = self.handle_client.handles["test-handle"]
            self._validateHandle(handle)

    def testRetrieveHandleRecord(self):
        with HTTMock(self.HandleMocks.view_handle_mock):
            handle = self.handle_client.retrieve_handle_record("test-handle")
            self._validateHandle(handle)

    def testViewHandleJSON(self):
        with HTTMock(self.HandleMocks.view_handle_mock):
            handle = self.handle_client.handles["test-handle"]
            self.assertIsNotNone(handle)
            jsons = str(handle)
            try:
                json.loads(jsons)
            except json.decoder.JSONDecodeError:
                self.fail("Invalid JSON representation")
            self.assertTrue('"id": "test-handle"' in jsons)

            jsons = str(handle.values[1])
            try:
                json.loads(jsons)
            except json.decoder.JSONDecodeError:
                self.fail("Invalid JSON representation")
            self.assertTrue('"id": "URL"' in jsons)
            self.assertTrue('"data_type": "string"' in jsons)
            self.assertTrue('"ttl": 86400' in jsons)
            self.assertTrue('"timestamp": "2026-01-07T18:47:40Z"' in jsons)
            self.assertTrue('"data": "https://www.example.com"' in jsons)

            jsons = str(handle.values[2])
            try:
                json.loads(jsons)
            except json.decoder.JSONDecodeError:
                self.fail("Invalid JSON representation")
            self.assertTrue('"id": "title"' in jsons)
            self.assertTrue('"data_type": "string"' in jsons)
            self.assertTrue('"ttl": 86400' in jsons)
            self.assertTrue('"timestamp": "2026-01-07T18:47:40Z"' in jsons)
            self.assertTrue('"data": "TEST"' in jsons)

            jsons = str(handle.values[3])
            try:
                json.loads(jsons)
            except json.decoder.JSONDecodeError:
                self.fail("Invalid JSON representation")
            self.assertTrue('"id": "description"' in jsons)
            self.assertTrue('"data_type": "string"' in jsons)
            self.assertTrue('"ttl": 86400' in jsons)
            self.assertTrue('"timestamp": "2026-01-07T18:47:40Z"' in jsons)
            self.assertTrue('"data": "A test handle"' in jsons)

            jsons = str(handle.values[4])
            try:
                json.loads(jsons)
            except json.decoder.JSONDecodeError:
                self.fail("Invalid JSON representation")
            self.assertTrue('"id": "HS_ADMIN"' in jsons)
            self.assertTrue('"data_type": "admin"' in jsons)
            self.assertTrue('"ttl": 86400' in jsons)
            self.assertTrue('"timestamp": "2026-01-07T18:47:40Z"' in jsons)
            self.assertTrue(
                    '"data": {"handle": "21.T99999/TESTUSER01", "index": 301, "permissions": "011111110011"}' in jsons
                    )

    def testGetHandleValueByIndex(self):
        with HTTMock(self.HandleMocks.view_handle_mock):
            handle = self.handle_client.handles["test-handle"]
            self.assertIsNotNone(handle)
            self.assertEqual(handle.values[1].id, "URL")

    def testGetHandleValueById(self):
        with HTTMock(self.HandleMocks.view_handle_mock):
            handle = self.handle_client.handles["test-handle"]
            self.assertIsNotNone(handle)
            self.assertEqual(handle.values["URL"].data, "https://www.example.com")

    def testGetValueFromHandle(self):
        with HTTMock(self.HandleMocks.view_handle_mock):
            val = self.handle_client.get_value_from_handle("test-handle", "URL")
            self.assertEqual(val, "https://www.example.com")
