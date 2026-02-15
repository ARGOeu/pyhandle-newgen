import json
import tempfile

from httmock import HTTMock

from pymod import HandleClient, HandleServiceException

from .handlemocks import HandleMocks, TestHandlesBase


class TestHandles(TestHandlesBase):
    def setUp(self):
        self.handle_client = HandleClient.withBasicAuth(
            "localhost/api/handles/21.T99999",
            "301:21.T99999/TESTUSER01",
            "s3cr3t")
        self.HandleMocks = HandleMocks()

    def testAuthFail(self):
        with HTTMock(self.HandleMocks.view_handle_mock):
            handle_client = HandleClient.withBasicAuth(
                "localhost/api/handles/21.T99999",
                "301:21.T99999/TESTUSER01",
                "S3CR3T")
            self.assertRaises(HandleServiceException, handle_client.retrieve_handle_record, "test-handle")

    def testViewHandle(self):
        with HTTMock(self.HandleMocks.view_handle_mock):
            handle = self.handle_client.handles["test-handle"]
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
            self.assertTrue('"name": "URL"' in jsons)
            self.assertTrue('"data_type": "string"' in jsons)
            self.assertTrue('"ttl": 86400' in jsons)
            self.assertTrue('"timestamp": "2026-01-07T18:47:40Z"' in jsons)
            self.assertTrue('"data": "https://www.example.com"' in jsons)

            jsons = str(handle.values[2])
            try:
                json.loads(jsons)
            except json.decoder.JSONDecodeError:
                self.fail("Invalid JSON representation")
            self.assertTrue('"name": "title"' in jsons)
            self.assertTrue('"data_type": "string"' in jsons)
            self.assertTrue('"ttl": 86400' in jsons)
            self.assertTrue('"timestamp": "2026-01-07T18:47:40Z"' in jsons)
            self.assertTrue('"data": "TEST"' in jsons)

            jsons = str(handle.values[3])
            try:
                json.loads(jsons)
            except json.decoder.JSONDecodeError:
                self.fail("Invalid JSON representation")
            self.assertTrue('"name": "description"' in jsons)
            self.assertTrue('"data_type": "string"' in jsons)
            self.assertTrue('"ttl": 86400' in jsons)
            self.assertTrue('"timestamp": "2026-01-07T18:47:40Z"' in jsons)
            self.assertTrue('"data": "A test handle"' in jsons)

            jsons = str(handle.values[4])
            try:
                json.loads(jsons)
            except json.decoder.JSONDecodeError:
                self.fail("Invalid JSON representation")
            self.assertTrue('"name": "HS_ADMIN"' in jsons)
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
            self.assertEqual(handle.values[1].name, "URL")

    def testGetHandleValueByName(self):
        with HTTMock(self.HandleMocks.view_handle_mock):
            handle = self.handle_client.handles["test-handle"]
            self.assertIsNotNone(handle)
            self.assertEqual(handle.values.by_name("URL")[0].data, "https://www.example.com")

    def testLoadFromJSONUserPass(self):
        with tempfile.NamedTemporaryFile(mode="w") as tf:
            tf.write(
                """{"handle_server_url": "https://localhost/api/handles/21.T99999","""
                """ "username":"301:21.T99999/TESTUSER01","""
                """ "password":"s3cr3t"}"""
                )
            tf.seek(0)
            HandleClient.withConfig(tf.name)
            tf.close()

    def testLoadFromJSONCertKey(self):
        with (
                tempfile.NamedTemporaryFile(mode="w") as tf,
                tempfile.NamedTemporaryFile() as cf,
                tempfile.NamedTemporaryFile() as kf
                ):
            tf.write(
                """{{"handle_server_url": "https://localhost/api/handles/21.T99999","""
                """ "certificate_only":"{0}","""
                """ "private_key":"{1}"}}""".format(cf.name, kf.name)
                )
            tf.seek(0)
            HandleClient.withConfig(tf.name)
            tf.close()
            cf.close()
            kf.close()

    def testLoadFromJSONCertOnly(self):
        with (
                tempfile.NamedTemporaryFile(mode="w") as tf,
                tempfile.NamedTemporaryFile() as cf
                ):
            tf.write(
                """{{"handle_server_url": "https://localhost/api/handles/21.T99999","""
                """ "certificate_and_key":"{0}"}}""".format(cf.name)
                )
            tf.seek(0)
            HandleClient.withConfig(tf.name)
            tf.close()
            cf.close()

    def testDeleteHandleStr(self):
        with HTTMock(self.HandleMocks.delete_handle_mock):
            self.handle_client.handles.delete("test-handle")

    def testDeleteHandleObj(self):
        with HTTMock(
                self.HandleMocks.view_handle_mock,
                self.HandleMocks.delete_handle_mock
                ):
            handle = self.handle_client.handles["test-handle"]
            self.handle_client.handles.delete(handle)

    def testDeleteHandleValueByIndex(self):
        with HTTMock(
                self.HandleMocks.view_handle_mock,
                self.HandleMocks.delete_handle_mock
                ):
            self.handle_client.handles["test-handle"].values.delete(
                    self.handle_client.handles["test-handle"].values[1]
                    )

    def testDeleteHandleValueByName(self):
        with HTTMock(
                self.HandleMocks.view_handle_mock,
                self.HandleMocks.delete_handle_mock
                ):
            self.handle_client.handles["test-handle"].values.delete(
                    self.handle_client.handles["test-handle"].values.by_name("URL")[0]
                    )

    def testDeleteHandleHSAdminValue(self):
        with HTTMock(
                self.HandleMocks.view_handle_mock,
                self.HandleMocks.delete_handle_mock
                ):
            v = self.handle_client.handles["test-handle"].values.by_name("HS_ADMIN")[0]
            self.assertRaises(Exception, self.handle_client.handles["test-handle"].values.delete, v)
