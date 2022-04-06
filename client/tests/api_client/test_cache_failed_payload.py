import client.src.api_client as api_client


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


def test_cache_failed_payload_1():
    payload_mock = {
        "vendor_id": 1,
        "product_id": 2
    }
    cache = CacheMock()
    config = ConfigMock()

    api_client._cache = cache
    api_client._config = config

    for _ in range(0, config.cache_max_entries + 1):
        api_client._cache_failed_payload(payload_mock)

    assert len(api_client._cache) == config.cache_max_entries


def test_cache_failed_payload_2():
    payload_mock = {
        "vendor_id": 1,
        "product_id": 2
    }
    cache = CacheMock()
    config = ConfigMock()

    api_client._cache = cache
    api_client._config = config
    count = int(config.cache_max_entries / 2)

    for _ in range(0, count):
        api_client._cache_failed_payload(payload_mock)

    assert len(api_client._cache) == count

