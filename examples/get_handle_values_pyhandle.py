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
    parser = ArgumentParser(description="Simple Argo HANDLE.net PYHANDLE compatibility fetch example")
    parser.add_argument("--creds", type=str, required=True, help="json credentials file")
    parser.add_argument("--handle", type=str, required=True, help="handle")
    parser.add_argument(
        "--https-verify",
        type=https_verify_arg,
        default=True,
        help="'true'/'false', or a path to a CA bundle file/dir. Defaults to true",
    )
    args = parser.parse_args()

    cred = PIDClientCredentials.load_from_JSON(args.creds)
    client = PyHandleClient('rest').instantiate_with_credentials(cred, HTTPS_verify=args.https_verify)

    try:
        handle = client.handles[args.handle]
        print("HANDLE:", handle.id)
        print("Values:")
        for v in handle.values:
            if v is None:
                continue
            print("[{0}]".format(v.id), v.name, "→", v.data)
    except HandleServiceException as e:
        if e.rc == 100:
            print("Service Error: handle `{0}' not found".format(args.handle), file=sys.stderr)
        else:
            print(e.msg, file=sys.stderr)
    except Exception as e:
        print("Unexpected error: ", repr(e), file=sys.stderr)
