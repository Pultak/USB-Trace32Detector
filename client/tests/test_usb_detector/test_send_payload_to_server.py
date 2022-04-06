import platform
import getpass
from unittest import mock
from datetime import datetime

import client.src.usb_detector.event_listener


@mock.patch('client.src.usb_detector.event_listener.send_data')
def test_send_payload_to_server_1(send_data_mock):
    device_mock = {
        "vendor_id": 1,
        "product_id": 2
    }
    metadata_mock = {
        "username": getpass.getuser(),
        "hostname": platform.uname().node,
        "timestamp": str(datetime.now()).split('.')[0]
    }
    status_mock = "connected"

    metadata_mock["device"] = device_mock
    metadata_mock["status"] = status_mock

    client.src.usb_detector.event_listener._send_payload_to_server(device_mock, status_mock)

    args = send_data_mock.call_args.args
    send_data_mock.assert_called()
    assert args[0] == metadata_mock
