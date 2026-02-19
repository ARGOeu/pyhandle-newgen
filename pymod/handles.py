from __future__ import annotations

import json
import logging
from typing import Union

from .restresource import RestResourceItem, RestResourceList

logger = logging.getLogger(__name__)


class Handles(RestResourceList):
    """Collection class for handles"""
    def _fetch_route(self):
        return None

    def _fetch_args(self) -> list:
        return []

    def _create_child(self, data: dict):
        return Handle(self, data)

    def _delete_route(self):
        return "delete_handle"

    def _add_route(self):
        return "register_handle"

    def _add_args(self):
        return [self.__add_handle]

    def add(self, item: RestResourceItem | dict | str):
        # FIXME: Map object value names to API value names
        # e.g. data_type -> format
        if isinstance(item, dict):
            data = item
            self.__add_handle = item["handle"]
            del data["handle"]
        elif isinstance(item, RestResourceItem):
            json_str = '{{"values": [{0}]}}'.format(', '.join(str(x) for x in getattr(item, 'values')))
            data = json.loads(json_str)
            self.__add_handle = item.id
            del data["id"]
        elif isinstance(item, str):
            data = json.loads(item)
            self.__add_handle = data["handle"]
            del data["handle"]
        else:
            raise TypeError("Unsupported parameter type")

        # Remove any values of "HS_ADMIN" type
        try:
            for i in reversed(range(len(data["values"]))):
                if data["values"][i]["type"] == "HS_ADMIN":
                    del data["values"][i]
        except Exception:
            pass

        # Add a proper "HS_ADMIN" value
        data["values"].append(self.__create_admin_entry())

        return super().add(data)

    def __create_admin_entry(self):
        '''
        Create an entry of type "HS_ADMIN".

        :return: The entry as a dict.
        '''
        # If the handle owner is specified, use it. Otherwise, use 200:0.NA/prefix
        # With the prefix taken from the handle that is being created, not from anywhere else.
        if self._parent._handle_owner is None:
            adminindex = 200
            prefix = self.__add_handle.split('/')[0]
            adminhandle = '0.NA/' + prefix
        else:
            split = self._parent._handle_owner.split(':')
            if len(split) == 2:
                try:
                    adminindex = int(split[0])
                except ValueError:
                    raise Exception("Invalid handle syntax for handle owner")
                adminhandle = split[1]
            elif len(split) == 1:
                adminindex = 200
                adminhandle = split[0]
            elif len(split) > 2:
                raise Exception("Invalid handle syntax for handle owner")

        data = {
                'value': {
                    'index': adminindex,
                    'handle': adminhandle,
                    'permissions': self._parent._admin_permissions
                    },
                'format': 'admin'
                }

        # FIXME: Find an index between [100, 200) not used by other provided values
        # instead of using a hard-coded value of 100
        index = 100
        entry = {'index': index, 'type': 'HS_ADMIN', 'data': data}

        # FIXME: support TTL for HS_ADMIN
        # if ttl is not None:
        #     entry['ttl'] = ttl

        return entry


class HandleValues(RestResourceList):
    """Collection class for handle values"""
    def __init__(self, parent: Handle):
        super().__init__(parent, 1)
        self._fetch()

    def _fetch(self):
        # Index 0 is special and reserved, append an empty value
        # to make the values OrderedDict 1-based
        self.update({0: None})
        for i in self._parent._x_vals:
            self.update({i["index"]: HandleValue(self, i)})
            self._page_count = 1
            self._current_page = 1

    def _fetch_route(self):
        return None

    def _fetch_args(self):
        return []

    def _create_child(self, data: dict):
        try:
            vid = data["__fetch__"]
        except Exception:
            raise KeyError("id")

        for i in self.items():
            if i[1] is None:
                continue
            if i[1].id == vid:
                return i[1]
        raise KeyError(data["__fetch__"])

    def _delete_args(self) -> list:
        return [self._parent.id]

    def _delete_route(self):
        return "delete_handle_value"

    def delete(self, item: Union[RestResourceItem, str]) -> RestResourceList:
        if (isinstance(item, str) and item == "HS_ADMIN") or (
                isinstance(item, HandleValue) and item.name == "HS_ADMIN"
                ):
            raise Exception("Illegal operation")
        else:
            return super().delete(item)

    def by_name(self, name: str) -> list[HandleValue] | None:
        """
        Return a list of HandleValue instances that match the provided 'name' argument.
        If no value matches, then None is returned
        """
        ret = []
        for i in self.items():
            if i[1] is None:
                continue
            if i[1].name == name:
                ret.append(i[1])
        if len(ret) == 0:
            return None
        else:
            return ret


class HandleValue(RestResourceItem):
    """Representation class for handle values"""
    def __init__(self, parent: HandleValues, data={}):
        super().__init__(parent, data)
        if data is not None:
            self._id = data["index"]
            self._name = data["type"]
            self._data_type = data["data"]["format"]
            self._data = data["data"]["value"]
            self._ttl = data["ttl"]
            self._timestamp = data["timestamp"]
            delattr(self, "type")

    def _fetch_route(self):
        return None

    def _fetch_args(self):
        return []

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, value):
        self._data_type = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def ttl(self):
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        self._ttl = value

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value


class Handle(RestResourceItem):
    """Representation class for handle entries"""
    def __init__(self, parent, data: dict):
        super().__init__(parent, data)
        delattr(self, "responseCode")
        delattr(self, "handle")

    def _fetch_route(self):
        return "get_handle_record"

    def _fetch_args(self) -> list:
        return [self.id]

    @property
    def values(self):
        return HandleValues(self)

    @values.setter
    def values(self, value):
        self._x_vals = value
