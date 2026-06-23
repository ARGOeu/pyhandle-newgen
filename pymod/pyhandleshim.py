import json
from typing import Optional

from .exceptions import HandleException
from .handleclient import HandleClient


class PIDClientCredentials(object):
    @staticmethod
    def load_from_JSON(json_filename: str):
        config = {}
        config["conf_file"] = json_filename
        with open(json_filename) as f:
            j = json.load(f)
        if "username" in j.keys() and "password" in j.keys():
            config["username"] = j["username"]
            config["password"] = j["password"]
        elif "private_key" in j.keys() and "certificate_only" in j.keys():
            config["certificate_only"] = j["certificate_only"]
            config["private_key"] = j["private_key"]
        elif "certificate_and_key" in j.keys():
            config["certificate_and_key"] = j["certificate_and_key"]
        else:
            raise HandleException("Malformed credentials file")
        if "handle_server_url" in j.keys():
            config["handle_server_url"] = j["handle_server_url"]
        if "prefix" in j.keys():
            config["prefix"] = j["prefix"]
        return PIDClientCredentials(config)

    def __init__(self, config: dict):
        self._config = config

    def get_server_URL(self) -> Optional[str]:
        return self._config.get("handle_server_url")

    def get_prefix(self) -> Optional[str]:
        return self._config.get("prefix")


class PyHandleClient(object):
    def __init__(self, client_type: str):
        if client_type == 'rest':
            pass
        else:
            raise ValueError("Supported client types: 'rest'")

    @staticmethod
    def instantiate_with_username_and_password(endpoint: str, username: str, password: str, **kwargs):
        return HandleClient.withBasicAuth(endpoint, username=username, password=password, **kwargs)

    @staticmethod
    def instantiate_with_credentials(creds: PIDClientCredentials, **kwargs):
        json_filename = creds._config["conf_file"]
        return HandleClient.withConfig(json_filename, **kwargs)
