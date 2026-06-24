#!/usr/bin/python
import sys
from argparse import ArgumentParser

from pyhandle_newgen import (HandleServiceException, PIDClientCredentials,
                             PyHandleClient)


def https_verify_arg(value):
    """Parse --https-verify: 'true'/'false' (bool) or a path to a CA bundle file/dir."""
    low = value.strip().lower()
    if low == "true":
        return True
    if low == "false":
        return False
    return value


if __name__ == "__main__":
    parser = ArgumentParser(description="Simple Argo HANDLE.net create example")
    parser.add_argument("--creds", type=str, required=True, help="json credentials file")
    parser.add_argument("--handle", type=str, required=True, help="handle")
    parser.add_argument("--url", type=str, required=True, help="handle url value")
    parser.add_argument("--key", type=str, required=False, action="append", help="optional extra handle value key")
    parser.add_argument("--val", type=str, required=False, action="append", help="optional extra handle value data")
    parser.add_argument(
        "--https-verify",
        type=https_verify_arg,
        default=True,
        help="'true'/'false', or a path to a CA bundle file/dir. Defaults to true",
    )
    args = parser.parse_args()

    if len(args.key or []) != len(args.val or []):
        print("key/val arguments must be given in pairs", file=sys.stderr)
        exit(1)

    cred = PIDClientCredentials.load_from_JSON(args.creds)
    client = PyHandleClient('rest').instantiate_with_credentials(cred, HTTPS_verify=args.https_verify)
    extra_types = {}

    try:
        if len(args.key or []) > 0:
            for i in range(len(args.key)):
                extra_types[args.key[i]] = {
                        "format": "string",
                        "value": args.val[i]
                        }
        client.register_handle(args.handle, args.url, overwrite=True, **extra_types)
    except HandleServiceException as e:
        print(e.msg, file=sys.stderr)
    except Exception as e:
        print("Unexpected error:", repr(e), file=sys.stderr)
