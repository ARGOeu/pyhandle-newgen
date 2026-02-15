#!/usr/bin/python
import sys
from argparse import ArgumentParser

from pyhandle_newgen import (HandleServiceException, PIDClientCredentials,
                             PyHandleClient)

if __name__ == "__main__":
    parser = ArgumentParser(description="Simple Argo HANDLE.net PYHANDLE compatibility fetch example")
    parser.add_argument("--creds", type=str, required=True, help="json credentials file")
    parser.add_argument("--handle", type=str, required=True, help="handle")
    args = parser.parse_args()

    cred = PIDClientCredentials.load_from_JSON(args.creds)
    client = PyHandleClient('rest').instantiate_with_credentials(cred)

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
