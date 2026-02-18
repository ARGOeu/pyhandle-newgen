import traceback

from .handleclient import HandleClient


def main():
    client = HandleClient.withBasicAuth(
        "{0}/{1}".format('hdl.grnet.gr:8001/api/handles', '21.T15999'),
            '301:21.T15999/TESTUSER08',
            'xxxxx',
        )
            # HS_ADMIN_permissions="011111110011",
    try:
        args = {
            "URL": {
                "format": "string",
                "value": "https://www.grnet.gr"
            },

            "title": {
                "format": "string",
                "value": "RAISE"
            },
            "description": {
                "format": "string",
                "value": "RAISE"
            },
        }

        resp = client.register_handle('test-handle-py-v10', 'https://www.grnet.gr', overwrite=True, **args)
        print(resp)
    except Exception as e:
        print("Error while registering handle: ", repr(e))
        traceback.print_exc()


if __name__ == "__main__":
    main()
