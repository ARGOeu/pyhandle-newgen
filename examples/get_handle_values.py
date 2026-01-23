#!/usr/bin/python
import sys
from argparse import ArgumentParser

from pyhandle_newgen import HandleClient, HandleServiceException

if __name__ == "__main__":
    parser = ArgumentParser(description="Simple Argo HANDLE.net fetch example")
    parser.add_argument(
        "--endpoint",
        type=str,
        required=True,
        help="FQDN[:port][/path] of Argo HANDLE.net Service API",
    )
    parser.add_argument("--prefix", type=str, required=True, help="HANDLE prefix")
    parser.add_argument("--username", type=str, required=True, help="username")
    parser.add_argument("--password", type=str, required=True, help="password")
    parser.add_argument("--handle", type=str, required=True, help="handle")
    parser.add_argument(
        "-f",
        help="treat password argument as a path to a file holding the actual password",
        action="store_true",
    )
    args = parser.parse_args()

    if args.f:
        try:
            with open(args.password, "r") as passfile:
                password = passfile.read().strip()
        except Exception as e:
            print("Error while reading password from file:", str(e), file=sys.stderr)
            exit(1)
    else:
        password = args.password

    client = HandleClient.instantiate_with_username_and_password(
            "{0}/{1}".format(args.endpoint, args.prefix),
            args.username,
            password
            )

    try:
        handle = client.handles[args.handle]
        print("HANDLE:", handle.id)
        print("Values:")
        for v in handle.values:
            if v is None:
                continue
            print("  ", v.id, "→", v.data)
    except HandleServiceException as e:
        if e.rc == 100:
            print("Service Error: handle `{0}' not found".format(args.handle), file=sys.stderr)
        else:
            print(e.msg, file=sys.stderr)
    except Exception as e:
        print("Unexpected error: ", repr(e), file=sys.stderr)
