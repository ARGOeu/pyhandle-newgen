import json
import tempfile

from httmock import HTTMock

from pymod import HandleBasicCreds, HandleClient, HandleCreds, HandleX509Creds

from .handlemocks import HandleMocks, TestHandlesBase


class TestHandles(TestHandlesBase):
    def setUp(self):
        self.handle_client = HandleClient.instantiate_with_username_and_password(
                "localhost/api/handles/21.T99999",
                "21.T99999/TESTUSER01",
                "s3cr3t")
        self.HandleMocks = HandleMocks()

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

    def testLoadFromJSONUserPass(self):
        with tempfile.NamedTemporaryFile(mode="w") as tf:
            tf.write('{"username":"21.T99999/TESTUSER01","password":"s3cr3t"}')
            tf.seek(0)
            creds = HandleCreds.load_from_JSON(tf.name)
            tf.close()
            assert isinstance(creds, HandleBasicCreds)

    def testLoadFromJSONCertKey(self):
        with (
                tempfile.NamedTemporaryFile(mode="w") as tf,
                tempfile.NamedTemporaryFile() as cf,
                tempfile.NamedTemporaryFile() as kf
                ):
            tf.write('{{"certificate_only":"{0}","private_key":"{1}"}}'.format(cf.name, kf.name))
            tf.seek(0)
            creds = HandleCreds.load_from_JSON(tf.name)
            tf.close()
            cf.close()
            kf.close()
            assert isinstance(creds, HandleX509Creds)

    def testLoadFromJSONCertOnly(self):
        with (
                tempfile.NamedTemporaryFile(mode="w") as tf,
                tempfile.NamedTemporaryFile() as cf
                ):
            tf.write('{{"certificate_and_key":"{0}"}}'.format(cf.name))
            tf.seek(0)
            creds = HandleCreds.load_from_JSON(tf.name)
            tf.close()
            cf.close()
            assert isinstance(creds, HandleX509Creds)
