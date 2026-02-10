import tempfile

from httmock import HTTMock

from pymod import HandleClient, PIDClientCredentials, PyHandleClient

from .handlemocks import HandleMocks, TestHandlesBase


class TestPyHandles(TestHandlesBase):
    def setUp(self):
        self.handle_client = PyHandleClient('rest').instantiate_with_username_and_password(
                "localhost/api/handles/21.T99999",
                "21.T99999/TESTUSER01",
                "s3cr3t")
        self.HandleMocks = HandleMocks()

    def testRetrieveHandleRecord(self):
        with HTTMock(self.HandleMocks.view_handle_mock):
            handle = self.handle_client.retrieve_handle_record("test-handle")
            self._validateHandle(handle)

    def testGetValueFromHandle(self):
        with HTTMock(self.HandleMocks.view_handle_mock):
            val = self.handle_client.get_value_from_handle("test-handle", "URL")
            self.assertEqual(val, "https://www.example.com")

    def testLoadFromJSON(self):
        with tempfile.NamedTemporaryFile(mode="w") as tf:
            tf.write('{"username":"21.T99999/TESTUSER01","password":"s3cr3t"}')
            tf.seek(0)
            cred = PIDClientCredentials.load_from_JSON(tf.name)
            client = PyHandleClient('rest').instantiate_with_credentials(cred)
            tf.close()
            assert isinstance(client, HandleClient)
