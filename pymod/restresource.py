import abc
import json
import logging
from collections import OrderedDict
from typing import Union

logger = logging.getLogger(__name__)


class RestResource(abc.ABC):
    """Base class for REST API responses"""

    def __init__(self, parent):
        """Initialize a REST response

        Args:
            parent(oject): a HandleClient object or another RestResource instance
        """
        self._parent = parent

    @property
    def handle_endpoint(self):
        return self._parent.handle_endpoint

    @property
    def connection(self):
        return self._parent.connection

    @property
    def id_name(self):
        """
        Return the JSON field name that identifies the resource.
        Defaults to "id", subclasses may need to override it.

        Id names for child resources (RestResourceItem) must be declared
        in the parent resource (RestResourceList), as the parent must know the id name
        beforehand, in order to populate the dictionary of children.

        Dotted paths are supported for JSON fields that are not at the top level of the data
        object returned by the API.

        The return value may also be a list, to denote a compound key. In that case, the
        key will consist of the values of the JSON fields, concatenated with an undercore.
        """
        return "id"

    @property
    def data_root(self):
        """
        Return the JSON field name that contains the resource data.
        Defaults to None, subclasses may need to override it
        """
        return None

    def _fetch_params(self) -> dict:
        """Method to provide values for querystring params on the GET REST route"""
        return {}


class RestResourceItem(RestResource):
    """Base class for REST API responses representing a single item"""

    def __init__(self, parent, data: dict):
        """
        Initialize a REST response item, setting properties from provided data dictionary.
        If the dictionary contains a single entry named "__fetch__" instead of actual response data,
        then the data will be fetched from the API.
        """
        logger.debug("Initing RestResourceItem object " + str(type(self)))
        self._parent = parent
        self.id = None
        if len(data) == 1 and data.get("__fetch__") is not None:
            self.id = data["__fetch__"]
            data = self._fetch()
            if self.data_root is not None:
                data_root_path = self.data_root.split(".")
                for i in data_root_path:
                    data = data[i]
                if type(data) is list:
                    data = data[0]
        if data is not None:
            for k in data:
                # logger.debug("setting " + k + " to " + (str(data[k]) or "<None>"))
                setattr(self, k, data[k])

    def __str__(self):
        """
        Return a JSON representation of the resource, recursivly.

        Internal properties starting with "_x_" will be excluded, as will
        "parent" and "_parent"
        """

        # Extract a dictonary of primitive properties
        d1 = {
            x: self.__dict__[x]
            for x in self.__dict__
            if not isinstance(self.__dict__[x], RestResource)
            and x not in {"_parent", "parent"} and not x.startswith("_x_")
        }
        while True:
            changed = False
            for k, v in d1.items():
                if k.startswith("__"):
                    del d1[k]
                    changed = True
                    break
                if k.startswith("_"):
                    d1[k[1:]] = v
                    del d1[k]
                    changed = True
                    break
            if not changed:
                break
        # Loop over properties that are RestResource instances (excluding "_parent")
        # and append their properties to the dictionary
        for x in self.__dict__:
            if isinstance(self.__dict__[x], RestResource) and x not in {"_parent"} and not x.startswith("_x_"):
                d2 = self.__dict__[x].__dict__
                del d2["_parent"]
                d1 = {**d1, x: d2}
        # Return a JSON representation of the built dictionary
        return json.dumps(d1, default=str)

    @abc.abstractmethod
    def _fetch_route(self) -> str:
        """Abstract method to be implemented by subclasses, to denote the REST API route for GET requests

        Should return the key from the parent service object route dict, that corresponds to the REST route
        """
        return ""

    @abc.abstractmethod
    def _fetch_args(self) -> list:
        """Abstract method to be implemented by subcasses, to provide values for params on the GET REST route"""
        return []

    def _fetch(self):
        """Fetch an entry from the REST API, using the fetch route denoted by self::_fetch_route"""
        logger.debug("FETCHING ITEM")
        res = self.connection.make_request(
            self.connection.routes[self._fetch_route()][1].format(
                self.handle_endpoint, *self._fetch_args()
            ),
            self._fetch_route(),
            self._fetch_params(),
        )
        return res


class RestResourceList(OrderedDict, RestResource):
    """
    Base class for REST API responses representing a paged list of items.

    Inherits OrderedDict to keep an internal dict of RestResourceItems when iterrating,
    and a separate cache dict to avoid re-fetching individual items.
    """

    def __init__(self, parent, page_size=1):
        logger.debug("Initing RestResourceList object " + str(type(self)))
        super(OrderedDict, self).__init__()
        super(RestResource, self).__init__()
        self._parent = parent
        self._page_size = page_size
        self._page_count = 1
        self._current_page = 0
        self._cache = OrderedDict()

    def refresh(self):
        """Clear the internal dict, the cache dict, and reset paging"""
        self.clear()
        self._cache.clear()
        self._current_page = 0
        self._page_count = 1
        return self

    def _add_route(self) -> str:
        """Abstract method to be implemented by subclasses, to denote the REST API route for POST requests

        Should return the key from the parent service object route dict, that corresponds to the REST route
        """
        raise Exception("Operation not supported or not implemented")

    def _add_args(self) -> list:
        """Abstract method to be implemented by subcasses, to provide values for params on the POST REST route"""
        raise Exception("Operation not supported or not implemented")

    @abc.abstractmethod
    def _fetch_route(self) -> str:
        """Abstract method to be implemented by subcasses, to denote the REST API route for GET requests

        Should return the key from the parent service object route dict, that corresponds to the REST route
        """
        return ""

    @abc.abstractmethod
    def _fetch_args(self) -> list:
        """Abstract method to be implemented by subcasses, to provide values for params on the GET REST route"""
        return []

    def _create_child(self, data: dict):
        """Abstract method to be implemented by subclasses, to create the appropriate RestResourceItem instance"""
        raise Exception("Operation not supported or not implemented")

    def _get_item_id(self, item):
        item_id = ""
        id_names = self.id_name
        if not type(id_names) is list:
            id_names = [id_names]
        # iterate id_name entries for compound IDs
        for id_name in id_names:
            # walk JSON structure if the id_name attribute is a dotted path
            id_path = id_name.split(".")
            if len(id_path) == 1:
                if type(item) is dict:
                    tmp_item_id = item[id_name]
                else:
                    tmp_item_id = getattr(item, id_name)
            else:
                tmp_item_id = item
                for j in id_path:
                    tmp_item_id = tmp_item_id[j]
            item_id = "{0}_{1}".format(item_id, tmp_item_id)
        return item_id.lstrip("_")

    def _fetch(self):
        """
        Fetch results from the REST API, using the fetch route denoted by self::_fetch_route

        Will fetch up to self::_page_size results each time, keeping track of the current page
        of results in self::_current_page
        """
        if self._fetch_route() is None:
            return
        logger.debug("FETCHING LIST")
        res = self.connection.make_request(
            self.connection.routes[self._fetch_route()][1].format(
                self.handle_endpoint, *self._fetch_args()
            ),
            self._fetch_route(),
            self._fetch_params(),
        )
        # hardcode page_count to 1, as the API does not support paging
        self._page_count = 1
        # Create a RestResourceItem for each JSON object in the response, and add it to the internal dict
        data_root = res
        if self.data_root is not None:
            data_root_path = self.data_root.split(".")
            for i in data_root_path:
                # workaround for paths enclosed in unary lists
                if type(data_root) is list:
                    if len(data_root) == 1:
                        data_root = data_root[0]
                    else:
                        raise RuntimeError("Non unary list detected while walking data root path")
                data_root = data_root.get(i)

        for i in data_root:
            item_id = self._get_item_id(i)
            self.update({str(item_id): self._create_child(i)})
        self._current_page += 1

    def __iter__(self):
        """Iterate over all results, using self::_fetch for each page"""
        self._current_page = 0
        logger.debug("ITERING")
        while self._current_page < self._page_count:
            self._fetch()
            logger.debug(
                "PAGE " + str(self._current_page) + " of " + str(self._page_count)
            )
            if len(self.items()) == 0:
                return None
            else:
                for i, j in enumerate(self.items()):
                    if i >= (self._current_page - 1) * self._page_size:
                        yield j[1]
        logger.debug("EOD")

    def __getitem__(self, id):
        """
        OrderedDict __getitem__ override.

        Checks if the internal dict has an item with the requested id, from an iteration.
        If not, check the cache. If there's no such item, attempt a fetch request and cache the item
        upon success
        """
        # try to fetch data if the internal dict is empty
        if len(self) == 0:
            self._fetch()

        if isinstance(id, int):
            item = list(self)[id]
        else:
            item = super(OrderedDict, self).get(id)
            if item is None:
                item = self._cache.get(id)
                if item is None:
                    item = self._create_child({"__fetch__": id})
                    if item is not None:
                        self._cache.update({self._get_item_id(item): item})
        return item

    def get(self, id, default=None):
        """
        OrderedDict get override. Calls __getitem__ but ignores errors and returns default value on failures, instead
        """
        tmp = None
        try:
            tmp = self.__getitem__(id)
        finally:
            return tmp or default

    def add(self, item: Union[RestResourceItem, dict, str]):
        """
        Creates a new subresource under the resource list

        This will issue an API request using the endpoint specified by the _add_route property,
        posting a JSON representation of the given item. If the request succeedes, the appropriate
        RestResourceItem subclassed object will be returned, populated with the response's data
        """
        if self._add_route != "":
            if isinstance(item, RestResourceItem):
                body = str(item)
            elif isinstance(item, dict):
                body = json.dumps(item)
            else:
                body = item
            res = self.connection.make_request(
                self.connection.routes[self._add_route()][1].format(
                    self.handle_endpoint, *self._add_args()
                ),
                self._add_route(),
                body=body,
            )
            ret = self._create_child(res)
            return ret
        else:
            raise Exception("Operation not supported or not implemented")

    def __str__(self):
        return "[{0}]".format(", ".join([str(x) for x in list(self)]))
