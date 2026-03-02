from __future__ import annotations

import json
import logging
from typing import Optional, Union

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
        return "delete_handle_record"

    def _add_route(self):
        return "register_handle"

    def _add_args(self):
        return [self.__add_handle]

    def add(self, item: RestResourceItem | dict | str):
        if isinstance(item, dict):
            data = item
            self.__add_handle = item["handle"]
            del data["handle"]
        elif isinstance(item, Handle):
            data = json.loads(item.to_hdl_json())
            self.__add_handle = item.id
            for i in reversed(range(len(data["values"]))):
                for j in reversed(range(len(data["values"][i].keys()))):
                    if data["values"][i][
                            list(data["values"][i].keys())[j]
                            ] is None:
                        del data["values"][i][
                                list(data["values"][i].keys())[j]
                                ]
            if "handle" in data.keys():
                del data["handle"]
        elif isinstance(item, str):
            data = json.loads(item)
            self.__add_handle = data["handle"]
            if hasattr(data, "handle"):
                del data["handle"]
        else:
            raise TypeError("Unsupported parameter type")

        # Do not allow explicitly setting HS_ADMIN
        for i in reversed(range(len(data["values"]))):
            if data["values"][i]["type"] == "HS_ADMIN":
                raise Exception("Illegal operation")

        # Add a proper "HS_ADMIN" value
        data["values"].append(self.__create_admin_entry())

        # Assign the proper index to each entry that does not have an index
        for entry in data["values"]:
            if entry.get("index") is None:
                entry_type = entry["type"]
                entry["index"] = self.__make_another_index(
                        data["values"], url=(entry_type == "URL"), hs_admin=(entry_type == "HS_ADMIN"))

        super().add(data)

        return self[self.__add_handle]

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

        entry = {'type': 'HS_ADMIN', 'data': data}

        return entry

    def __make_another_index(self, list_of_entries, url=False, hs_admin=False):
        """
        Find an index not yet used in the handle record and not reserved for
            any (other) special type.

        :param: list_of_entries: List of all entries to find which indices are
            used already.
        :param url: If True, an index for an URL entry is returned (1, unless
            it is already in use).
        :param hs_admin: If True, an index for HS_ADMIN is returned (100 or one
            of the following).
        :return: An integer.
        """

        start = 2

        # reserved indices:
        reserved_for_url = {1}
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
                if entry.get("index") is not None:
                    existing_indices.add(int(entry['index']))

        # find new index:
        all_prohibited_indices = existing_indices | prohibited_indices
        search_max = max(start, max(all_prohibited_indices)) + 2
        for index in range(start, search_max):
            if index not in all_prohibited_indices:
                return index


class HandleValues(RestResourceList):
    """Collection class for handle values"""
    def __init__(self, parent: Handle):
        self._initialized = False
        super().__init__(parent, 1)
        self._fetch()
        self._initialized = True

    def _fetch(self):
        # Index 0 is special and reserved, append an empty value
        # to make the values OrderedDict 1-based
        self.update({0: None})
        if hasattr(self._parent, "_x_vals"):
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

    def by_name(self, name: str):
        """
        Return a list of HandleValue instances that match the provided 'name' argument.
        If no value matches, then None is returned
        """
        for i in self.items():
            if i[1] is None:
                continue
            if i[1].name == name:
                # ret.append(i[1])
                yield i[1]
        return None

    def add(self, item: RestResourceItem | dict | str, idx: int = 0, overwrite: bool = True):
        if idx == 0:
            new_idx = 0
            last_idx = 0
            if len(self.items()) == 0:
                new_idx = 1
            else:
                for i in self.items():
                    if last_idx > 0 and i[1].id > last_idx + 1:
                        break
                    if i[1] is not None and i[1].id >= new_idx:
                        new_idx = i[1].id + 1
                    if i[1] is not None:
                        last_idx = i[1].id
        elif idx >= 1 and idx < 100:
            new_idx = idx
        else:
            raise Exception("Invalid index requested for new string value")

        if isinstance(item, dict):
            new_val = HandleValue(self, item)
        elif isinstance(item, HandleValue):
            item._parent = self
            new_val = item
        elif isinstance(item, str):
            new_val = HandleValue(self, json.loads(item))
        else:
            raise TypeError("Unsupported parameter type")

        new_val._id = new_idx
        new_val._tainted = True
        new_val.update(overwrite)
        self.update({new_idx: new_val})


class HandleValue(RestResourceItem):
    """Representation class for handle values"""
    def __init__(self, parent: Optional[HandleValues] = None, data={}):
        super().__init__(parent, data)
        if data is not None:
            self._id = data["index"] if "index" in data.keys() else None
            self._name = data["type"] if "type" in data.keys() else None
            self._data_type = data["data"]["format"] if (
                    "data" in data.keys() and "format" in data["data"].keys()
                    ) else None
            self._data = data["data"]["value"] if "data" in data.keys() and "value" in data["data"].keys() else None
            self._ttl = data.get("ttl")
            self._timestamp = data.get("timestamp")
            if hasattr(data, "type"):
                delattr(self, "type")
        self._tainted = False

    def _fetch_route(self):
        return None

    def _fetch_args(self):
        return []

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if self._parent is None or self._parent._initialized:
            raise Exception("Illegal operation")
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        if self._parent is None or self._parent._initialized:
            self._tainted = True

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, value):
        self._data_type = value
        if self._parent is None or self._parent._initialized:
            self._tainted = True

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        if self._parent is None or self._parent._initialized:
            self._tainted = True

    @property
    def ttl(self):
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        self._ttl = value
        if self._parent is None or self._parent._initialized:
            self._tainted = True

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value
        if self._parent is None or self._parent._initialized:
            self._tainted = True

    def to_hdl_json(self) -> str:
        """Return a HANDLE JSON representation of the handle record value"""
        d = {
            "index": self.id,
            "type": self.name,
            "data": {
                "format": self.data_type or "string",
                "value": self.data
                },
            "ttl": self.ttl,
            "timestamp": self.timestamp
            }
        if d["ttl"] is None:
            del d["ttl"]
        if d["timestamp"] is None:
            del d["timestamp"]
        return json.dumps(d)

    def _serialize(self) -> str:
        if self.name == "HS_ADMIN":
            return "null"
        else:
            return self.to_hdl_json()

    @property
    def tainted(self) -> bool:
        return self._tainted

    def _update_route(self):
        return "update_handle_value"

    def _update_args(self) -> list:
        return [self._parent._parent.id, self.id, self.__overwrite]

    def update(self, overwrite: bool = True):
        self.__overwrite = overwrite
        if self._parent is None:
            raise Exception("Object has not been assigned to a parent")
        if self.tainted:
            super().update()


class Handle(RestResourceItem):
    """Representation class for handle entries"""
    def __init__(self, parent: Optional[Handles] = None, data: dict = {}):
        super().__init__(parent, data)
        if self.id is None:
            self.id = data.get("handle")
        for i in ["responseCode", "handle"]:
            if hasattr(self, i):
                delattr(self, i)
        self._handle_values: Optional[HandleValues] = None

    def _fetch_route(self):
        return "get_handle_record"

    def _fetch_args(self) -> list:
        return [self.id]

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def values(self):
        if self._handle_values is None:
            self._handle_values = HandleValues(self)
        return self._handle_values

    @values.setter
    def values(self, value):
        self._x_vals = value

    def to_hdl_json(self) -> str:
        """Return a HANDLE JSON representation of the handle record and all its values"""
        return json.dumps({
            "handle": self.id,
            "values": [json.loads(x.to_hdl_json()) for x in self.values if x is not None]
            })

    def _serialize(self) -> str:
        ro_vals = ["HS_ADMIN"]
        return json.dumps({
            "handle": self.id,
            "values": [json.loads(x._serialize()) for x in self.values if (
                (x is not None) and (x.type not in ro_vals) and x.tainted)]
            })

    def _update_route(self):
        return "update_handle_record"

    def _update_args(self) -> list:
        return [self.id]

    @property
    def tainted(self) -> bool:
        for i in self.values:
            if i is not None and i.tainted:
                return True
        return False

    def update(self):
        if self.tainted:
            super().update()
