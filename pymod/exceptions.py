from typing import Union


class HandleException(Exception):
    """Base exception class for all Handle service related errors"""

    def __init__(self, *args, **kwargs):
        super(HandleException, self).__init__(*args, **kwargs)


class HandleServiceException(HandleException):
    """Exception for Handle Service API errors"""

    def __init__(self, json, request):
        errord: dict[str, Union[str, int]] = {}

        if json.get("message"):
            self.msg = "While trying [{0}]: {1}".format(request, json["message"])
            errord.update(error=self.msg)
        else:
            self.msg = "Unknown error"

        if json.get("response_code"):
            self.rc = json["response_code"]
            errord.update(response_code=self.rc)
        else:
            self.rc = 0

        if json.get("code"):
            self.code = json["code"]
            errord.update(status_code=self.code)
        else:
            self.code = 0

        super(HandleServiceException, self).__init__(errord)


class HandleTimeoutException(HandleServiceException):
    """Exception for timeouts errors

    Timeouts can come from the load balancer for partial requests that were not
    completed in the required time frame.
    """

    def __init__(self, json, request):
        super(HandleTimeoutException, self).__init__(json, request)


class HandleConnectionException(HandleException):
    """Exception for connection related problems caught from requests library"""

    def __init__(self, exp, request):
        self.msg = "While trying the [{0}]: {1}".format(request, repr(exp))
        super(HandleConnectionException, self).__init__(self.msg)
