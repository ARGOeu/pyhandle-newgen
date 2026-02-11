from __future__ import annotations

import logging

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

    def _delete_route(self):
        # TODO
        raise NotImplementedError


class HandleValue(RestResourceItem):
    def __init__(self, parent: HandleValues, data={}):
        super().__init__(parent, data)
        if data is not None:
            self._index = data["index"]
            self._id = data["type"]
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
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

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
