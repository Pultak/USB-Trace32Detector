import client.src.api_client

from unittest import mock


@mock.patch('client.src.api_client._init_cache')
def test_api_client_set_config_1(_init_cache_mock):
    class Config:
        def __init__(self):
            self.server_url = "127.0.0.1"
            self.server_port = "54444"
            self.server_endpoint = "/api/v1/usb-logs"

    config = Config()
    client.src.api_client.api_client_set_config(config)

    assert client.src.api_client._config is config
    assert client.src.api_client._uri == "127.0.0.1:54444/api/v1/usb-logs"
