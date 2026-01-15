from os import path

from setuptools import setup

NAME = "pyhandle-newgen"

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md")) as f:
    long_description = f.read()


def get_ver():
    try:
        with open(NAME + ".spec") as f:
            for line in f:
                if "Version:" in line:
                    return line.split()[1]
    except IOError:
        print("Make sure that %s is in directory" % (NAME + ".spec"))
        raise SystemExit(1)


REQUIREMENTS = ["requests"]

setup(
    name=NAME,
    version=get_ver() or "Unknown",
    author="GRNET",
    author_email="wvkarageorgos@admin.grnet.gr",
    license="ASL 2.0",
    description="A simple python library for interacting with the ARGO HANDLE.net service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    tests_require=["setuptools_scm", "httmock", "pytest"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    url="https://github.com/ARGOeu/pyhandle-newgen",
    package_dir={"pyhandle_newgen": "pymod/"},
    packages=["pyhandle_newgen"],
    install_requires=REQUIREMENTS,
)
