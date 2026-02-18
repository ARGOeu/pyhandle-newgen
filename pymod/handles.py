from __future__ import annotations

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
        print("Initializing HandleValue with data:", data)
        if data is not None:
            self._id = data["index"]
            self._name = data["type"]
            self._type = data["data"]["format"]
            self._data = data["data"]["value"]
            self._ttl = data.get("ttl", 86400)
            self._timestamp = data.get("timestamp","")
            delattr(self, "type")

    def to_dict(self) -> dict:
        return {
            "index": self._id,
            "type": self._name,
            "data": {
                "format": self._type,
                "value": self._data
            },
            "ttl": self._ttl,
            "timestamp": self._timestamp
        }

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
        return self._type

    @data_type.setter
    def data_type(self, value):
        self._type = value

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
        # delattr(self, "responseCode")
        # delattr(self, "handle")

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
