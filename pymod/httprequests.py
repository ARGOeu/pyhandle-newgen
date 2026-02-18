import json
import logging
import socket
import urllib.parse

import requests

from .exceptions import (HandleConnectionException, HandleServiceException,
                         HandleTimeoutException)

logger = logging.getLogger(__name__)


class HttpRequests(object):
    """Class for HTTP requests to the Handle Service API"""

    def __init__(self, parent):
        self._parent = parent
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
                "delete",
                "https://{0}/{1}",
            ],
            "delete_handle_value": [
                "delete",
                "https://{0}/{1}?index={2}",
            ],
        }

    def _handle_rc_to_str(self, rc):
        rc_dict = {
                "1": "Success",
                "2": "Error",
                "3": "Server Too Busy",
                "4": "Protocol Error",
                "5": "Operation Not Supported",
                "6": "Recursion Count Too High",
                "7": "Server Read-only",
                "100": "Handle Not Found",
                "101": "Handle Already Exists",
                "102": "Invalid Handle",
                "200": "Values Not Found",
                "201": "Value Already Exists",
                "202": "Invalid Value",
                "300": "Out of Date Site Info",
                "301": "Server Not Responsible",
                "302": "Service Referral",
                "303": "Prefix Referral",
                "400": "Invalid Admin",
                "401": "Insufficient Permissions",
                "402": "Authentication Needed",
                "403": "Authentication Failed",
                "404": "Invalid Credential",
                "405": "Authentication Timed Out",
                "406": "Authentication Error",
                "500": "Session Timeout",
                "501": "Session Failed",
                "502": "Invalid Session Key",
                "504": "Invalid Session Setup Request",
                "505": "Session Duplicate Msg Rejected"
                }
        try:
            msg = rc_dict[str(rc)]
        except Exception:
            msg = "Unknown Error"

        return msg

    def _error_dict(self, response_content, status):
        try:
            if status == 200 or status == 201:
                error_dict = json.loads(response_content) if response_content else dict()
            else:
                response = json.loads(response_content) if response_content else dict()
                error_dict = {
                        "code": status,
                        "response_code": response.get("responseCode") or 0,
                        "message": self._handle_rc_to_str(response.get("responseCode")),
                        "details": response.get("message", "Unknown Error")
                        }
        except ValueError:
            error_dict = {"code": status, "response_code": "0", "message": "Unknown Error"}

        return error_dict

    def make_request(
        self, url, route_name, params=None, body=None, **reqkwargs
    ) -> dict:
        """Common method for PUT, GET, POST HTTP requests with appropriate service error handling"""
        m = self.routes[route_name][0]
        decoded = None
        try:
            reqmethod = getattr(requests, m)
            logger.debug(
                "doing a "
                + reqmethod.__name__
                + " request on "
                + url
                + " with params "
                + str(params)
            )
            if self._parent.auth_mode == 0:
                r = reqmethod(
                        url,
                        json=body,
                        params=params,
                        auth=requests.auth.HTTPBasicAuth(
                            urllib.parse.quote_plus(self._parent._creds["username"]),
                            urllib.parse.quote_plus(self._parent._creds["password"])),
                        **reqkwargs
                        )
            elif self._parent.auth_mode == 1:
                if self._parent._creds.get("key") is not None:
                    cert = (self._parent._creds["crt"], self._parent._creds["key"])
                else:
                    cert = self._parent._creds["crt"]
                r = reqmethod(
                        url, json=body, params=params, cert=cert,
                        **reqkwargs)
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
                        content or json.dumps({"responseCode": "403"}),
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
