#!/usr/bin/python
import sys
from argparse import ArgumentParser

from pyhandle_newgen import HandleClient, HandleServiceException, HandleValue

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
    grp1 = parser.add_mutually_exclusive_group(required=True)
    grp1.add_argument("--idx", type=int, help="index of handle value to delete. Either 'idx' or 'name' is required")
    grp1.add_argument("--name", type=str, help="name of handle value to delete. Either 'idx' ir 'name' is required")
    parser.add_argument(
        "-f",
        help="treat password argument as a path to a file holding the actual password",
        action="store_true",
    )
    parser.add_argument(
        "-y",
        help="assume yes to all questions",
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

    client = HandleClient.withBasicAuth(
            "{0}/{1}".format(args.endpoint, args.prefix),
            username=args.username,
            password=password
            )

    try:
        handle = client.handles[args.handle]
        values: list[HandleValue] = []
        if args.idx is not None:
            for i in handle.values:
                if i is not None and i.id == args.idx:
                    values.append(i)
        else:
            values = handle.values.by_name(args.name) or []

        if values is None or len(values) == 0:
            raise IndexError()

        for v in values:
            if not args.y:
                print("Value at index", v.id, "of handle", handle.id, "will be deleted:")
                print()
                print("HANDLE:", handle.id)
                print("Value at index", v.id, ":", v.name, "→", v.data)
                print()
                do_del = input("Are you sure? [y/N] ")
            else:
                do_del = "y"
            if do_del == "y":
                handle.values.delete(v)
                print("Value at index", args.idx, "deleted")
            else:
                print("Delete operation aborted")
    except HandleServiceException as e:
        if e.rc == 100:
            print("Service Error: handle `{0}' not found".format(args.handle), file=sys.stderr)
        else:
            print(e.msg, file=sys.stderr)
    except IndexError:
        if args.idx is not None:
            print("Error: no handle value at index", args.idx, "found")
        else:
            print("Error: no handle values matching the name '{0}' found".format(args.name))
    except Exception as e:
        print("Unexpected error: ", repr(e), file=sys.stderr)
