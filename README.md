# pyhandle-newgen

ARGO HANDLE.net library: A simple python library for interacting with the ARGO HANDLE.net service 

## Library installation

The library been tested with Python versions 3.9, 3.11, and 3.12 on Rocky 9. In order to install the library, you'll need to check out the source, have python setuptools installed and run

```bash
python3 ./setup.py build && \
  sudo python3 ./setup.py install
```

Alternatively, on RHEL-based systems with rpm-build and python3-dev installed, you may run

```bash
mkdir -p ~/rpmbuild/SOURCES && \
  python3 ./setup.py build && \
  python3 ./setup.py bdist_rpm && \
  cp dist/pyhandle-newgen-0.1.0.tar.gz && \
  rpmbuild -bb pyhandle-newgen.spec
```

to create an RPM file for each supported python version under ~/rpmbuild/RPMS/noarch, and then use rpm / dnf to install the desired RPM packages, e.g.

```bash
sudo dnf install ~/rpmbuild/RPMS/noarch/python3-pyhandle-newgen-0.1.0-1.el9.noarch.rpm
```

for version `0.1.0-1` of the library using the default (platform) python.

## Authentication

The Argo HANDLE.net library supports authentication via a username/password combination or via x509 credentials. For username/password authentication, a client object may be initialized as follows:

```python
from pyhandle_newgen import HandleClient
client = HandleClient.instantiate_with_username_and_password(
        "hdl.grnet.gr:8001/api/handles/PREFIX",
        "PREFIX/USER",
        "PASSWORD"
        )
```

## Examples

In the `examples` folder, you may find the following library usage examples:

* retrieving a HANDLE record and printing its values
* retrieving a HANDLE record and printing its values, using [PYHANDLE](https://docs.eudat.eu/b2handle/fordevelopers_pyhandle/) syntax
* deleting a HANDLE record
* deleting a HANDLE record's value
* registering a new HANDLE record
* registering a new HANDLE record, using [PYHANDLE](https://docs.eudat.eu/b2handle/fordevelopers_pyhandle/) syntax
* adding a new value to a HANDLE record
* updating a single HANDLE value
* updating a HANDLE record

### Retrieving a HANDLE record and printing its values

```bash
python3 ./examples/get_handle_values.py --endpoint FQDN[:PORT]/PATH --prefix THE_HANDLE_PREFIX --username THE_USERNAME --password PATH_TO_PWD_FILE -f --handle THE_HANDLE_ID [--json]
```

replacing capitalized tokens with proper values, e.g. `python3 ./examples/get_handle_values.py --endpoint hdl.grnet.gr:8001/api/handles --prefix 21.T99999 --username 21.T99999/TESTUSER01 --password ~/.hdlpass -f --handle test-handle. If the optional `json` argument is given, then the output will be a HANDLE formatted JSON string.

### Retrieving a HANDLE record and printing its values, using PYHANDLE syntax

```bash
python3 ./examples/get_handle_values_pyhandle.py --endpoint FQDN[:PORT]/PATH --creds PATH_TO_CREDENTIALS_JSON_FILE --handle THE_HANDLE_ID
```

replacing capitalized tokens with proper values, e.g. `python3 ./examples/get_handle_values.py --creds ~/hdl_creds.json --handle test-handle

### Deleting a HANDLE record

```bash
python3 ./examples/delete_handle.py --endpoint FQDN[:PORT]/PATH --prefix THE_HANDLE_PREFIX --username THE_USERNAME --password PATH_TO_PWD_FILE -f --handle THE_HANDLE_ID
```

replacing capitalized tokens with proper values, as in the first example.

### Deleting a HANDLE record's value

```bash
python3 ./examples/delete_handle_value.py --endpoint FQDN[:PORT]/PATH --prefix THE_HANDLE_PREFIX --username THE_USERNAME --password PATH_TO_PWD_FILE -f --handle THE_HANDLE_ID --idx THE_VALUE_INDEX
```

replacing capitalized tokens with proper values, as in the previous examples.

### Registering a new HANDLE record

```bash
python3 ./examples/add_handle.py --endpoint FQDN[:PORT]/PATH --prefix THE_HANDLE_PREFIX --username THE_USERNAME --password PATH_TO_PWD_FILE -f [--owner THE_HANDLE_OWNER] --handle THE_HANDLE_ID --url URL 
```

replacing capitalized tokens with proper values, as in the previous examples. Here, the optional `owner` argument will be used to set the new handle's `HS_ADMIN record`, if specified, otherwise the default `200:0.NA/PREFIX` value will be used.

### Registering a new HANDLE record using PYHANDLE syntax

```bash
python3 ./examples/add_handle_pyhandle.py --endpoint FQDN[:PORT]/PATH --creds PATH_TO_CREDENTIALS_JSON_FILE --handle THE_HANDLE_ID --url URL [--key KEY1 --val VAL1 ...]
```

replacing capitalized tokens with proper values, as in the previous examples. Here, the optional `key` and `val` arguments may be used in pairs, in order to provide extra handle string-formated values to be added during creation.

### Adding a new value to a HANDLE record

```bash
python3 ./examples/add_handle_value.py --endpoint FQDN[:PORT]/PATH --prefix THE_HANDLE_PREFIX --username THE_USERNAME --password PATH_TO_PWD_FILE -f --handle THE_HANDLE_ID --name VALUE_NAME --data VALUE_DATA [--idx VALUE_INDEX] [--force]
```

replacing capitalized tokens with proper values, as in the previous examples. Here, the `name` and `data` arguments will be used to add a new `string` value, while the optional `idx` argument will be used for the new handle value index, if specified, otherwise the first available index between [1, 100) will be used. The optional `force` argument will allow overwriting an existing value, otherwise an error will be raised. Note that this is intentionally the opposite of the library's default behavior -- where existing values get overridden by default -- in order to highlight the option's function.

### Updating a single HANDLE value

```bash
python3 ./examples/update_handle_url.py --endpoint FQDN[:PORT]/PATH --prefix THE_HANDLE_PREFIX --username THE_USERNAME --password PATH_TO_PWD_FILE -f --handle THE_HANDLE_ID --name VALUE_NAME --data VALUE_DATA
```

replacing capitalized tokens with proper values, as in the previous examples. Here, the `name` and `data` arguments will be used to update the first occurance of any exising `string` value by the given name; if no such value exists, an exception will be raised.

### Updating a HANDLE record

```bash
python3 ./examples/update_handle_url.py --endpoint FQDN[:PORT]/PATH --prefix THE_HANDLE_PREFIX --username THE_USERNAME --password PATH_TO_PWD_FILE -f --handle THE_HANDLE_ID --name VALUE_NAME --data VALUE_DATA
```

replacing capitalized tokens with proper values, as in the previous examples. In this example, the code iterates all existing handle values and looks for string-typed values starting with `http://`. Any such values found will be updated, changing `http://` to `https://`, by using a single call to the API after the iteration, which will include only the changed values.

## Environment variables

* `DEBUG`: Set to any truthy value in order to have debugging information printed to stdout; useful for development pusposes.
