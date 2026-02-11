from __future__ import annotations

import json
from typing import Optional

from .exceptions import HandleException
from .handles import Handles
from .httprequests import HttpRequests


class HandleClient(object):
    """Module main class, to access the REST API"""

    def __init__(self, **kwargs):
        """
        General purpose contructor, called by static constructor methods
        """
        if kwargs.get("endpoint") is None:
            raise HandleException("Missing required initialization argument 'endpoint'")
        if kwargs.get("username") is not None and kwargs.get("password") is not None:
            self.auth_mode = 0
            self._creds = {
                    "username": kwargs["username"],
                    "password": kwargs["password"]
                    }
            self._conn = HttpRequests(self)
        elif kwargs.get("certificate_only") is not None and kwargs.get("private_key") is not None:
            self.auth_mode = 1
            self._creds = {
                    "crt": kwargs["certificate_only"],
                    "key": kwargs["private_key"]
                    }
            self._conn = HttpRequests(self)
        elif kwargs.get('certificate_and_key') is not None:
            self.auth_mode = 1
            self._creds = {"crt": kwargs["certificate_and_key"]}
            self._conn = HttpRequests(self)
        else:
            raise HandleException("Unsupported authentication method")

        self._handle_prefix = kwargs.get("prefix")
        self._handle_endpoint = kwargs["endpoint"]
        if self._handle_prefix is not None:
            if not self._handle_endpoint.endswith(self._handle_prefix):
                self._handle_endpoint = "{0}/{1}".format(self._handle_endpoint, self._handle_prefix)
        self._handle_owner = kwargs.get("handleowner")
        self._handles: Optional[Handles] = None

    @classmethod
    def withConfig(cls, config_filename: str, **kwargs):
        """
        Initialize a HandleClient from a JSON config file, optionally specifying
        additional configuration parameters. Parameters passed in kwargs will override
        those in the config file, if present
        """
        try:
            with open(config_filename, 'r')as config_file:
                j = json.loads(config_file.read())
                return cls(
                        endpoint=kwargs.get('handle_server_url') or j.get('handle_server_url'),
                        prefix=kwargs.get('prefix') or j.get('prefix'),
                        username=kwargs.get('username') or j.get('username'),
                        password=kwargs.get('password') or j.get('password'),
                        private_key=kwargs.get('private_key') or j.get('private_key'),
                        certificate_only=kwargs.get('certificate_only') or j.get('certificate_only'),
                        certificate_and_key=kwargs.get('certificate_and_key') or j.get('certificate_and_key'),
                        handleowner=kwargs.get('handleowner') or j.get('handleowner')
                        )
        except OSError as e:
            raise HandleException("Unable to load configuration file: {0}".format(repr(e)))
        except Exception as e:
            raise HandleException("Unexpected error while loading configuration: {0}".format(repr(e)))

    @classmethod
    def withBasicAuth(cls, endpoint: str, username: str, password: str, **kwargs):
        """
        Initialize a HandleClient which will use Basic Authentication
        """
        return cls(
                endpoint=endpoint,
                username=username,
                password=password,
                **kwargs
                )

    @classmethod
    def withX509Auth(cls, endpoint: str, cert: str, key: Optional[str], **kwargs):
        """
        Initialize a HandleClient which will use x509 Authentication

        If no key file is provided, the cert file is expected to hold
        the combined certificate and key
        """
        return cls(
                endpoint=endpoint,
                cert=cert,
                key=key,
                **kwargs
                )

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
        """PYHANDLE compatibility function"""
        return self.handles[handle]

    def get_value_from_handle(self, handle: str, key: str):
        """PYHANDLE compatibility function"""
        return self.handles[handle].values[key].data

    def delete_handle(self, handle: str):
        """PYHANDLE compatibility function"""
        return self.handles.delete(handle)
