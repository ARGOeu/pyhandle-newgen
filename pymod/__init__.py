import logging
import os

from .exceptions import (HandleConnectionException, HandleException,
                         HandleServiceException, HandleTimeoutException)
from .handleclient import (HandleBasicCreds, HandleClient, HandleCreds,
                           HandleX509Creds)
from .handles import Handle, Handles
from .pyhandleshim import PIDClientCredentials, PyHandleClient

logger = logging.getLogger(__name__)
if os.getenv("DEBUG") is not None and str(os.getenv("DEBUG")).lower() in [
    "1",
    "t",
    "true",
    "y",
    "yes",
]:
    import sys

    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)
else:
    logger.addHandler(logging.NullHandler())

__all__ = [
    "HandleBasicCreds",
    "HandleCreds",
    "HandleX509Creds",
    "HandleClient",
    "HandleConnectionException",
    "HandleException",
    "HandleServiceException",
    "HandleTimeoutException",
    "Handles",
    "Handle",
    "PIDClientCredentials",
    "PyHandleClient"
]
