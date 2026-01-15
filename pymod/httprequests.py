import json
import logging
import socket

import requests

from .exceptions import (HandleConnectionException, HandleServiceException,
                         HandleTimeoutException)

logger = logging.getLogger(__name__)


class HttpRequests(object):
    """Class for HTTP requests to the Handle Service API"""

    def __init__(self, parent):
        self.parent = parent
        self.routes = {
            "list_handles": [
                "get",
                "https://{0}?prefix={1}",
            ],
            "register_handle": [
                "put",
                "https://{0}/{1}",
            ],
            "get_handle_record": [
                "get",
                "https://{0}/{1}",
            ],
            "get_handle_value": [
                "get",
                "https://{0}/{1}?index={2}",
            ],
            "update_handle": [
                "post",
                "https://{0}/{1}",
            ],
            "delete_handle": [
                "get",
                "https://{0}/{1}",
            ],
        }

    def _error_dict(self, response_content, status):
        try:
            error_dict = json.loads(response_content) if response_content else dict()
        except ValueError:
            error_dict = {"error": {"code": status, "message": response_content}}

        return error_dict

    def make_request(
        self, url, route_name, params=None, body=None, **reqkwargs
    ) -> dict:
        """Common method for PUT, GET, POST HTTP requests with appropriate service error handling"""
        m = self.routes[route_name][0]
        decoded = None
        try:
#            # populate all requests with the X-Api-Key apikey header
#            # if there is no defined headers dict in the reqkwargs, introduce it
#            if "headers" not in reqkwargs:
#                headers = {
#                    "X-Api-Key": "{0}".format(self.apikey),
#                    "Accept": "application/json"
#                }
#                reqkwargs["headers"] = headers
#            else:
#                # if the there are already other headers defined, just append the X-Api-Key one
#                reqkwargs["headers"]["X-Api-Key"] = "{0}".format(self.apikey)

            reqmethod = getattr(requests, m)
            logger.debug(
                "doing a "
                + reqmethod.__name__
                + " request on "
                + url
                + " with params "
                + str(params)
            )
            if self.parent.auth_mode == 0:
                r = reqmethod(url, data=body, params=params, auth=requests.auth.HTTPBasicAuth(self.parent._creds.username, self.parent._creds.password), **reqkwargs)
            elif self.parent.auth_mode == 1:
                #TODO
                raise NotImplementedError()
            else:
                raise Exception("Unsupported authentication method")

            content = r.content
            status_code = r.status_code

            logger.debug("STATUS CODE:" + str(status_code))
            if status_code == 200 or status_code == 201:
                decoded = self._error_dict(content, status_code)

            # handle authn/z related errors for all calls
            elif status_code == 401 or status_code == 403:
                raise HandleServiceException(
                    json=self._error_dict(
                        content or json.dumps({"message": "Auth failure"}),
                        status_code,
                    ),
                    request=route_name,
                )

            elif status_code == 408:
                raise HandleTimeoutException(
                    json=self._error_dict(content, status_code), request=route_name
                )

            # handle any other erroneous behaviour by raising exception
            else:
                raise HandleServiceException(
                    json=self._error_dict(content, status_code), request=route_name
                )

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            socket.error,
        ) as e:
            raise HandleConnectionException(e, route_name)

        else:
            return decoded if decoded else {}
