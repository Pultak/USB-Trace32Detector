from client.src.usb_detector import api_client

import requests
from unittest import mock


@mock.patch('client.src.usb_detector.api_client._cache_failed_payload')
def test_send_data_1(_cache_failed_payload_mock):
    payload_mock = {
        "device": {
            "vendor_id": 1,
            "product_id": 2
        }
    }

    api_client._uri = None
    api_client.send_data(payload_mock)

    args = _cache_failed_payload_mock.call_args.args
    _cache_failed_payload_mock.assert_called()
    assert args[0] == payload_mock


@mock.patch('client.src.usb_detector.api_client._cache_failed_payload')
def test_send_data_2(_cache_failed_payload_mock):
    payload_mock = {
        "device": {
            "vendor_id": 1,
            "product_id": 2
        }
    }

    api_client._uri = "127.0.0.1:54444/api/v1/usb-logs"
    api_client.send_data(payload_mock)

    args = _cache_failed_payload_mock.call_args.args
    _cache_failed_payload_mock.assert_called()
    assert args[0] == payload_mock


@mock.patch('client.src.usb_detector.api_client.requests.post')
@mock.patch('client.src.usb_detector.api_client._cache_failed_payload')
def test_send_data_3(_cache_failed_payload_mock, post_mock):
    payload_mock = {
        "device": {
            "vendor_id": 1,
            "product_id": 2
        }
    }

    api_client._uri = "127.0.0.1:54444/api/v1/usb-logs"
    api_client.send_data(payload_mock)

    _cache_failed_payload_mock.assert_not_called()


@mock.patch('client.src.usb_detector.api_client.requests.post')
@mock.patch('client.src.usb_detector.api_client._cache_failed_payload')
def test_send_data_4(_cache_failed_payload_mock, post_mock):
    payload_mock = {
        "device": {
            "vendor_id": 1,
            "product_id": 2
        }
    }
    post_mock.side_effect = requests.exceptions.HTTPError()

    api_client._uri = "127.0.0.1:54444/api/v1/usb-logs"
    api_client.send_data(payload_mock)

    args = _cache_failed_payload_mock.call_args.args
    _cache_failed_payload_mock.assert_called()
    assert args[0] == payload_mock
