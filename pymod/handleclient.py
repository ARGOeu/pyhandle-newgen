from __future__ import annotations

import json
import os
from typing import Optional, Union

from .exceptions import HandleException
from .handles import Handles
from .httprequests import HttpRequests


class HandleCreds(object):
    @staticmethod
    def load_from_JSON(cred_file: str) -> HandleCreds:
        with open(cred_file) as f:
            j = json.load(f)
        if "username" in j.keys() and "password" in j.keys():
            return HandleBasicCreds(j["username"], j["password"])
        elif "private_key" in j.keys() and "certificate_only" in j.keys():
            return HandleX509Creds(j["certificate_only"], j["private_key"])
        elif "certificate_and_key" in j.keys():
            return HandleX509Creds(j["certificate_and_key"], None)
        else:
            raise HandleException("Malformed credentials file")


class HandleBasicCreds(HandleCreds):
    def __init__(self, username, password, **kwargs):
        self.username = username
        self.password = password

    @staticmethod
    def load_from_json(self, json_filename: str):
        j = json.loads(open(json_filename, 'r').read())
        self.client = j.get('client', 'rest')
        self.handle_server_url = j.get('handle_server_url')
        self.username = j.get('username')
        self.password = j.get('password')
        self.prefix = j.get('prefix')
        self.handleowner = j.get('handleowner')
        self.private_key = j.get('private_key')
        self.certificate_only = j.get('certificate_only')
        self.certificate_and_key = j.get('certificate_and_key')


class HandleX509Creds(HandleCreds):
    def __init__(self, cert_path: str, key_path: Optional[str], **kwargs):
        OK = os.path.isfile(cert_path) and os.access(cert_path, os.R_OK)
        if key_path is not None:
            OK = OK and (os.path.isfile(key_path) and os.access(key_path, os.R_OK))
        if not OK:
            raise HandleException("Unable to find or access certificate or key file.")
        else:
            self.crt = cert_path
            self.key = key_path


class HandleClient(object):
    """Module main class, to access the REST API"""

    def __init__(self, endpoint: str, creds: HandleCreds):
        self._handle_endpoint = endpoint
        self._conn = HttpRequests(self)
        self._handles: Optional[Handles] = None
        self._creds = creds
        if isinstance(creds, HandleBasicCreds):
            self.auth_mode = 0
        elif isinstance(creds, HandleX509Creds):
            self.auth_mode = 1
        else:
            raise HandleException("Unsupported authentication method")

    @classmethod
    def instantiate_with_username_and_password(cls, endpoint: str, username: str, password: str):
        return cls(endpoint, HandleBasicCreds(username, password))

    @classmethod
    def instantiate_with_certificate(cls, endpoint: str, cert_path: str, key_path: str):
        return cls(endpoint, HandleX509Creds(cert_path, key_path))

    @classmethod
    def instantiate_with_credentials(cls, endpoint: str, creds: Union[str, HandleCreds]):
        if isinstance(creds, str):
            return cls(endpoint, HandleCreds.load_from_JSON(creds))
        else:
            return cls(endpoint, creds)

    @property
    def handles(self) -> Handles:
        self._handles = self._handles or Handles(self)
        return self._handles

    @property
    def connection(self):
        return self._conn

    @property
    def handle_endpoint(self):
        return self._handle_endpoint

    def retrieve_handle_record(self, handle: str):
        return self.handles[handle]

    def get_value_from_handle(self, handle: str, key: str):
        return self.handles[handle].values[key].data
