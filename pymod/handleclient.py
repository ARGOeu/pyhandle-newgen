from __future__ import annotations

import json
from typing import Optional, Union

from .exceptions import (HandleException,
                         HandleAlreadyExistsException,
                         HandleSyntaxError, IllegalOperationException)
from .handles import Handles, Handle, HandleValues, HandleValue
from .httprequests import HttpRequests
import logging

logger = logging.getLogger(__name__)


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
        return self.handles[handle].values.by_name(key)[0].data

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
        '''
        Registers a new Handle with given name. If the handle already exists
        and overwrite is not set to True, the method will throw an
        exception.
        Note: This is just a wrapper for register_handle_kv. It was made for
        legacy reasons, as this library was created to replace an earlier
        library that had a method with specifically this signature.

        Note 2: It allows to pass (additionally to the handle name) a
        mandatory URL, and optionally a CHECKSUM, and more types as
        key-value pairs. Old method, made for legacy reasons, as this library
        was created to replace an earlier library that had a method with
        specifically this signature.

        :param handle: The full name of the handle to be registered (prefix
            and suffix)
        :param location: The URL of the data entity to be referenced
        :param checksum: Optional. The checksum string.
        :param extratypes: Optional. Additional key value pairs such as: additional_URLs for 10320/loc
        :param additional_URLs: Optional. A list of URLs (as strings) to be
            added to the handle record as 10320/LOC entry. Note: This is currently
            not implemented.
        :param overwrite: Optional. If set to True, an existing handle record
            will be overwritten. Defaults to False.
        :raises: :exc:`~pyhandle.handleexceptions.HandleAlreadyExistsException` Only if overwrite is not set or
            set to False.
        :raises: :exc:`~pyhandle.handleexceptions.HandleAuthenticationError`
        :raises: :exc:`~pyhandle.handleexceptions.HandleSyntaxError`
        :return: The handle name.
        '''

        if 'auth' in extratypes:
            logger.debug('Found keyword "auth", which will be registered as a key-value-pair in the handle record.')
            # TODO: Is this behaviour desired?

        if extratypes is None:
            extratypes = {}

        if  location is not None:
            extratypes["URL"] = {"format": "string", "value": location}

        if  checksum is not None:
            extratypes["CHECKSUM"] = {"format": "string", "value": checksum}

        if additional_URLs is not None:
            raise NotImplementedError('No support for argument "additional_URLs"!')

        print("extratypes: ", extratypes)

        return self.register_handle_kv(
            handle,
            overwrite,
            **extratypes
        )

    def register_handle_kv(self, handle, overwrite=False, **kv_pairs):
        """
        Registers a new Handle with given name. If the handle already exists
        and overwrite is not set to True, the method will throw an
        exception.

        :param handle: The full name of the handle to be registered (prefix
            and suffix)
        :param kv_pairs: The key value pairs to be included in the record,
            e.g. URL, CHECKSUM, ...
        :param overwrite: Optional. If set to True, an existing handle record
            will be overwritten. Defaults to False.
        :raises: :exc:`~pyhandle.handleexceptions.HandleAlreadyExistsException` Only if overwrite is not set or
            set to False.
        :raises: :exc:`~pyhandle.handleexceptions.HandleAuthenticationError`
        :raises: :exc:`~pyhandle.handleexceptions.HandleSyntaxError`
        :return: The handle name.
        """
        logger.debug('register_handle_kv...')

        if 'auth' in kv_pairs:
            logger.debug('Found keyword "auth", which will be registered as a key-value-pair in the handle record.')
            # TODO: Is this behaviour desired?

        # If already exists and can't be overwritten:
        if not overwrite:
            existing_record = self.retrieve_handle_record(handle)
            if existing_record is not None:
                logger.error('Could not register handle as it already exists and overwrite is not set to True.')
                raise HandleAlreadyExistsException

        # Create admin entry
        list_of_entries = []
        admin_entry = self.__create_admin_entry(
            self._handle_owner,
            self._admin_permissions,
            self.__make_another_index(list_of_entries, hs_admin=True),
            handle
        )
        list_of_entries.append(admin_entry)

        # Create other entries
        print("kv pairs: ", kv_pairs)
        if kv_pairs is not None:
            for key, value in kv_pairs.items():
                is_url = True if key == 'URL' else False
                entry = self.__create_entry(
                    key,
                    value,
                    self.__make_another_index(list_of_entries, is_url)
                )
                list_of_entries.append(entry)


        handle = Handle(self.handles, {'values': list_of_entries})
        handle_values = HandleValues(handle)
        for entry in list_of_entries:
            handle_value = HandleValue(parent=handle_values, data=entry)
            print("handle_value: ", handle_value.__str__())
        print(handle.__dict__)
        print(handle_values.__dict__)
        # return
        #
        #         for entry in list_of_entries:
        #             print("entry: ", entry)
        #             print(handle_value.__str__())
        # return
        # Create record itself and put to server:
        return self.__handle_registering(handle, list_of_entries)

    def __handle_registering(self, handle, list_of_entries):
        print("in here")
        url = self.connection.routes['register_handle'][1].format(self.handle_endpoint, handle)
        logger.debug(url)
        print(url)
        print("----------")
        print(handle.values)
        print("----------")
        fb = {"values":  list_of_entries}
        print(fb)
        print("------------")
        return self.connection.make_request(
            url=url,
            route_name='register_handle',
            body=fb
        )

    def __make_another_index(self, list_of_entries, url=False, hs_admin=False):
        '''
        Find an index not yet used in the handle record and not reserved for
            any (other) special type.

        :param: list_of_entries: List of all entries to find which indices are
            used already.
        :param url: If True, an index for an URL entry is returned (1, unless
            it is already in use).
        :param hs_admin: If True, an index for HS_ADMIN is returned (100 or one
            of the following).
        :return: An integer.
        '''

        start = 2

        # reserved indices:
        reserved_for_url = set([1])
        reserved_for_admin = set(range(100, 200))
        prohibited_indices = reserved_for_url | reserved_for_admin

        if url:
            prohibited_indices = prohibited_indices - reserved_for_url
            start = 1
        elif hs_admin:
            prohibited_indices = prohibited_indices - reserved_for_admin
            start = 100

        # existing indices
        existing_indices = set()
        if list_of_entries is not None:
            for entry in list_of_entries:
                existing_indices.add(int(entry['index']))

        # find new index:
        all_prohibited_indices = existing_indices | prohibited_indices
        searchmax = max(start, max(all_prohibited_indices)) + 2
        for index in range(start, searchmax):
            if index not in all_prohibited_indices:
                return index

    def __create_entry(self, entrytype, data, index, ttl=None):
        '''
        Create an entry of any type except HS_ADMIN.

        :param entrytype: THe type of entry to create, e.g. 'URL' or
            'checksum' or ... Note: For entries of type 'HS_ADMIN', please
            use __create_admin_entry().
        :param data: The actual value for the entry. Can be a simple string,
            e.g. "example", or a dict {"format":"string", "value":"example"}.
        :param index: The integer to be used as index.
        :param ttl: Optional. If not set, the library's default is set. If
            there is no default, it is not set by this library, so Handle
            System sets it.
        :return: The entry as a dict.
        '''

        if entrytype == 'HS_ADMIN':
            op = 'creating HS_ADMIN entry'
            msg = 'This method can not create HS_ADMIN entries.'
            raise IllegalOperationException(operation=op, msg=msg)

        entry = {'index': index, 'type': entrytype, 'data': data}

        if ttl is not None:
            entry['ttl'] = ttl
        print("#############")
        print("new entry: ", entry)
        print("#############")
        return entry

    def __create_admin_entry(self, handleowner, permissions, index, handle, ttl=None):
        '''
        Create an entry of type "HS_ADMIN".

        :param username: The username, i.e. a handle with an index
            (index:prefix/suffix). The value referenced by the index contains
            authentcation information, e.g. a hidden entry containing a key.
        :param permissions: The permissions as a string of zeros and ones,
            e.g. '0111011101011'. If not all twelve bits are set, the remaining
            ones are set to zero.
        :param index: The integer to be used as index of this admin entry (not
            of the username!). Should be 1xx.
        :param ttl: Optional. If not set, the library's default is set. If
            there is no default, it is not set by this library, so Handle
            System sets it.
        :return: The entry as a dict.
        '''
        # If the handle owner is specified, use it. Otherwise, use 200:0.NA/prefix
        # With the prefix taken from the handle that is being created, not from anywhere else.
        if handleowner is None:
            adminindex = '200'  # TODO Why string, not integer?
            prefix = handle.split('/')[0]
            adminhandle = '0.NA/' + prefix
            # TODO: Why is adminindex string, not integer? When I retrieve from
            # HandleSystem API, the JSON has an int there.
        else:
            adminindex, adminhandle = self.remove_index_from_handle(handleowner)

        data = {
            'value': {
                'index': adminindex,
                'handle': adminhandle,
                'permissions': permissions
            },
            'format': 'admin'
        }

        entry = {'index': index, 'type': 'HS_ADMIN', 'data': data}
        if ttl is not None:
            entry['ttl'] = ttl

        return entry

    def remove_index_from_handle(self, handle_with_index):
        '''
        Returns index and handle separately, in a tuple.

        :handle_with_index: The handle string with an index (e.g.
            500:prefix/suffix)
        :return: index and handle as a tuple, where index is integer.
        '''

        split = handle_with_index.split(':')
        if len(split) == 2:
            split[0] = int(split[0])
            return split
        elif len(split) == 1:
            return None, handle_with_index
        elif len(split) > 2:
            raise HandleSyntaxError(
                msg='Too many colons',
                handle=handle_with_index,
                expected_syntax='index:prefix/suffix')
