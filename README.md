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

### Retrieving a HANDLE record and printing its values

```bash
python3 ./examples/get_handle_values.py --endpoint FQDN[:PORT]/PATH --prefix=THE_HANDLE_PREFIX --username=THE_USERNAME --password=PATH_TO_PWD_FILE -f --handle=THE_HANDLE_ID
```

replacing capitalized tokens with proper values, e.g. `python3 ./examples/get_handle_values.py --endpoint hdl.grnet.gr:8001/api/handles --prefix=21.T99999 --username=21.T99999/TESTUSER01 --password=~/.hdlpass -f --handle=test-handle
`

## Environment variables

* `DEBUG`: Set to any truthy value in order to have debugging information printed to stdout, for development pusposes.
