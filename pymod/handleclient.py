from __future__ import annotations

import json
from typing import Optional, Union

from .exceptions import HandleException
from .handles import Handles, HandleValue
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
        self._admin_permissions = kwargs.get("admin_permissions", "011111110011")
        # HTTPS_verify: True | False | path-to-CA-bundle. Defaults to True.
        # Normalize None (missing, or passed explicitly e.g. from withConfig) to True,
        # while preserving an explicit False or a CA-bundle path string.
        verify = kwargs.get("HTTPS_verify")
        self._https_verify = True if verify is None else verify
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
                # HTTPS_verify must NOT use the `or` idiom: an explicit False would be
                # silently discarded. Prefer kwargs, fall back to file, else None
                # (which __init__ normalizes to the default True).
                if kwargs.get('HTTPS_verify') is not None:
                    https_verify = kwargs.get('HTTPS_verify')
                else:
                    https_verify = j.get('HTTPS_verify')
                return cls(
                        endpoint=kwargs.get('handle_server_url') or j.get('handle_server_url'),
                        prefix=kwargs.get('prefix') or j.get('prefix'),
                        username=kwargs.get('username') or j.get('username'),
                        password=kwargs.get('password') or j.get('password'),
                        private_key=kwargs.get('private_key') or j.get('private_key'),
                        certificate_only=kwargs.get('certificate_only') or j.get('certificate_only'),
                        certificate_and_key=kwargs.get('certificate_and_key') or j.get('certificate_and_key'),
                        handleowner=kwargs.get('handleowner') or j.get('handleowner'),
                        admin_permissions=kwargs.get('admin_permissions') or j.get('admin_permissions'),
                        HTTPS_verify=https_verify
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
        return list(self.handles[handle].values.by_name(key))[0].data

    def delete_handle(self, handle: str):
        """PYHANDLE compatibility function"""
        return self.handles.delete(handle)

    def delete_handle_value(self, handle: str, key: Union[list, str]):
        """PYHANDLE compatibility function"""
        h = self.handles[handle]
        if not isinstance(key, list):
            keys = [key]
        else:
            keys = key
        for k in keys:
            values = h.values.by_name(k)
            for v in values:
                h.values.delete(v)

    def register_handle(self, handle, location, checksum=None, additional_URLs=None, overwrite=False, **extratypes):
        """PYHANDLE compatibility function"""

        if not overwrite and self.retrieve_handle_record(handle) is not None:
            raise Exception("Handle already exists, cannot overwrite")

        if additional_URLs is not None:
            raise NotImplementedError('No support for argument "additional_URLs"!')

        values = list()
        location_value = {
                "type": "URL",
                "data": {
                    "format": "string",
                    "value": location
                    }
                }
        values.append(location_value)

        if checksum is not None:
            checksum_value = {
                    "type": "CHECKSUM",
                    "data": {
                        "format": "string",
                        "value": checksum
                        }
                    }
            values.append(checksum_value)

        if extratypes is not None:
            for key, value in extratypes.items():
                values.append({"type": key, "data": value})

        data = {"handle": handle, "values": values}
        return self.handles.add(data)

    def add_handle_value(self, handle, ttl=None, **kvpairs):
        """PYHANDLE compatibility function"""
        for key, newval in kvpairs.items():
            h = self.handles[handle]
            v = HandleValue()
            v.name = key
            v.data = newval
            if ttl is not None:
                v.ttl = ttl
            h.values.add(v, overwrite=False)

    def modify_or_add_handle_value(self, handle, ttl=None, **kvpairs):
        """PYHANDLE compatibility function"""
        for key, newval in kvpairs.items():
            h = self.handles[handle]
            v = HandleValue()
            v.name = key
            v.data = newval
            if ttl is not None:
                v.ttl = ttl
            h.values.add(v, overwrite=True)

    def modify_handle_value_not_add(self, handle, ttl=None, **kvpairs):
        """PYHANDLE compatibility function"""
        for key, newval in kvpairs.items():
            h = self.handles[handle]
            v = HandleValue()
            v.name = key
            v.data = newval
            if ttl is not None:
                v.ttl = ttl
            if len(list(h.values.by_name(key))) > 0:
                h.values.add(v, overwrite=True)
            else:
                raise Exception("Cannot modify unexisting handle")
            h.values.add(v, overwrite=True)

    def modify_handle_value(self, handle, ttl=None, add_if_not_exist=True, **kvpairs):
        """PYHANDLE compatibility function"""
        for key, newval in kvpairs.items():
            h = self.handles[handle]
            v = HandleValue()
            v.name = key
            v.data = newval
            if ttl is not None:
                v.ttl = ttl
            if not add_if_not_exist:
                if len(list(h.values.by_name(key))) > 0:
                    h.values.add(v, overwrite=True)
                else:
                    raise Exception("Cannot modify unexisting handle")
            h.values.add(v, overwrite=True)
