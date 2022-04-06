from client.src.usb_detector import api_client

from unittest import mock


class CacheMock:

    def __init__(self):
        self._data = []

    def pop(self):
        return self._data.pop()

    def append(self, payload):
        self._data.append(payload)

    def __len__(self):
        return len(self._data)


class ConfigMock:

    def __init__(self):
        self.cache_max_entries = 5
        self.max_retries = 3


payload_mock = {
    "device": {
        "vendor_id": 1,
        "product_id": 2
    }
}


@mock.patch('client.src.usb_detector.api_client.send_data')
def test_resend_cached_payloads_1(send_data_mock):
    cache = CacheMock()
    config = ConfigMock()

    api_client._cache = cache
    api_client._config = config

    for _ in range(0, config.cache_max_entries + 1):
        api_client._cache_failed_payload(payload_mock)

    api_client._resend_cached_payloads()
    send_data_mock.assert_called()
    assert len(api_client._cache) == 2

    api_client._resend_cached_payloads()
    assert len(api_client._cache) == 0

    api_client._resend_cached_payloads()
    assert len(api_client._cache) == 0


@mock.patch('client.src.usb_detector.api_client.send_data')
def test_resend_cached_payloads_2(send_data_mock):
    cache = CacheMock()
    config = ConfigMock()

    api_client._cache = cache
    api_client._config = config

    api_client._resend_cached_payloads()
    send_data_mock.assert_not_called()
    assert len(api_client._cache) == 0


@mock.patch('client.src.usb_detector.api_client.send_data')
def test_resend_cached_payloads_3(send_data_mock):
    cache = CacheMock()
    config = ConfigMock()

    api_client._cache = cache
    api_client._config = config

    for _ in range(0, 2):
        api_client._cache_failed_payload(payload_mock)

    assert len(api_client._cache) == 2
    api_client._resend_cached_payloads()
    send_data_mock.assert_called()
    assert len(api_client._cache) == 0

