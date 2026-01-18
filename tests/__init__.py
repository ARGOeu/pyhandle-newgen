import logging
import os

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
