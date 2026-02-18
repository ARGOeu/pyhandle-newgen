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

        if json.get("details"):
            self.error = json["details"]
            errord.update(details=self.error)

        super(HandleServiceException, self).__init__(errord)


class HandleTimeoutException(HandleServiceException):
    """Exception for timeouts errors

    Timeouts can come from the load balancer for partial requests that were not
    completed in the required time frame.
    """

    def __init__(self, json, request):
        super(HandleTimeoutException, self).__init__(json, request)

class HandleConflictException(HandleServiceException):
    """Exception for conflict  errors

    Conflicts can come from attempts to create a handle that already exists
    """

    def __init__(self, json, request):
        super(HandleConflictException, self).__init__(json, request)


class HandleConnectionException(HandleException):
    """Exception for connection related problems caught from requests library"""

    def __init__(self, exp, request):
        self.msg = "While trying the [{0}]: {1}".format(request, repr(exp))
        super(HandleConnectionException, self).__init__(self.msg)

class IllegalOperationException(HandleException):
    """
    To be raised when the user tries to create a HS_ADMIN self.handle,
    when he wants to create or remove 10320/loc entries using the
    wrong method, ...
    """
    def __init__(self, **args):

        # Default message:
        self.msg = "Illegal Operation"

        # Possible arguments:
        optional_args = ['msg', 'handle', 'operation']
        add_missing_optional_args_with_value_none(args, optional_args)
        self.handle = args['handle']
        self.custom_message = args['msg']
        self.operation = args['operation']

        if self.operation is not None:
            self.msg += ' ('+self.operation+')'
        if self.handle is not None:
            self.msg += ' on handle '+self.handle
        if self.custom_message is not None:
            self.msg += ': ' + self.custom_message
        self.msg += '.'

        super(self.__class__, self).__init__(self.msg)


class GenericHandleError(HandleException):
    """
    To be raised when the Handle Server returned an unexpected status code
    that does not map to any other specific exception.
    """
    def __init__(self,**args):

        # Default message:
        self.msg = 'Error during interaction with Handle Server'

        # Possible arguments:
        optional_args = ['msg', 'handle','response', 'payload', 'operation']
        add_missing_optional_args_with_value_none(args, optional_args)
        self.handle = args['handle']
        self.custom_message = args['msg']
        self.response = args['response']
        self.operation = args['operation']
        self.payload = args['payload']

        if self.operation is not None:
            self.msg += ' ('+self.operation+')'

        if self.custom_message is not None:
            self.msg += ': '+self.custom_message
        self.msg += '.'

        if self.handle is not None:
            self.msg += '\n\tHandle: '+self.handle

        if self.response is not None:
            self.msg += '\n\tURL: '+str(self.response.request.url)
            self.msg += '\n\tHTTP Status Code: '+str(self.response.status_code)
            self.msg += '\n\tResponse: '+str(self.response.content)

        if self.payload is not None:
            self.msg += '\n\tPayload: '+self.payload

        super(self.__class__, self).__init__(self.msg)

def add_missing_optional_args_with_value_none(args, optional_args):
    """
    Adds key-value pairs to the passed dictionary, so that
        afterwards, the dictionary can be used without needing
        to check for KeyErrors.

    If the keys passed as a second argument are not present,
        they are added with None as a value.

    :args: The dictionary to be completed.
    :optional_args: The keys that need to be added, if
        they are not present.
    :return: The modified dictionary.
    """

    for name in optional_args:
        if not name in args.keys():
            args[name] = None
    return args

class HandleSyntaxError(HandleException):
    '''
    To be raised if the Handle does not have correct syntax.
    '''
    def __init__(self, **args):

        # Default message:
        self.msg = 'Handle does not have expected syntax'

        # Possible arguments:
        optional_args = ['msg', 'handle','expected_syntax']
        add_missing_optional_args_with_value_none(args, optional_args)
        self.handle = args['handle']
        self.custom_message = args['msg']
        self.expected_syntax = args['expected_syntax']

        if self.handle is not None:
            self.msg = self.msg.replace('andle', 'andle '+self.handle)

        if self.custom_message is not None:
            self.msg += ': '+self.custom_message
        self.msg += '.'

        if self.expected_syntax is not None:
            self.msg += '\n\tExpected: '+self.expected_syntax

        super(self.__class__, self).__init__(self.msg)

class HandleAlreadyExistsException(HandleException):
    '''
    To be raised if self.handle already exists.
    '''
    def __init__(self, **args):

        # Default message:
        self.msg = 'Handle already exists'

        # Possible arguments:
        optional_args = ['msg', 'handle']
        add_missing_optional_args_with_value_none(args, optional_args)
        self.handle = args['handle']
        self.custom_message = args['msg']

        if self.handle is not None:
            self.msg = self.msg.replace('andle', 'andle '+self.handle)

        if self.custom_message is not None:
            self.msg += ': '+self.custom_message
        self.msg += '.'

        super(self.__class__, self).__init__(self.msg)