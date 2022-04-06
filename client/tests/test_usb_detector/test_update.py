from unittest import mock
from unittest.mock import Mock

from client.src.usb_detector import detector


@mock.patch('client.src.usb_detector.detector._store_connected_devices')
@mock.patch('client.src.usb_detector.detector.read_connected_devices', return_value=[1, 2, 3])
def test_update_1(read_connected_devices_mock, _store_connected_devices_mock):
    connected_mocks = [Mock() for _ in range(10)]
    detector._listeners_connected = [listener_mock.listener for listener_mock in connected_mocks]

    disconnected_mocks = [Mock() for _ in range(10)]
    detector._listeners_disconnected = [listener_mock.listener for listener_mock in disconnected_mocks]

    detector._update()
    assert detector._last_connected_devices == [1, 2, 3]
    for listener_mock in connected_mocks:
        listener_mock.listener.assert_called()
    for listener_mock in disconnected_mocks:
        listener_mock.listener.assert_not_called()


@mock.patch('client.src.usb_detector.detector._store_connected_devices')
@mock.patch('client.src.usb_detector.detector.read_connected_devices', return_value=[1, 2, 3])
def test_update_1(read_connected_devices_mock, _store_connected_devices_mock):
    detector._last_connected_devices = [1, 2, 3]
    connected_mocks = [Mock() for _ in range(10)]
    detector._listeners_connected = [listener_mock.listener for listener_mock in connected_mocks]

    disconnected_mocks = [Mock() for _ in range(10)]
    detector._listeners_disconnected = [listener_mock.listener for listener_mock in disconnected_mocks]

    detector._update()
    assert detector._last_connected_devices == [1, 2, 3]
    for listener_mock in connected_mocks:
        listener_mock.listener.assert_not_called()
    for listener_mock in disconnected_mocks:
        listener_mock.listener.assert_not_called()


@mock.patch('client.src.usb_detector.detector._store_connected_devices')
@mock.patch('client.src.usb_detector.detector.read_connected_devices', return_value=[])
def test_update_1(read_connected_devices_mock, _store_connected_devices_mock):
    detector._last_connected_devices = [1, 2, 3]
    connected_mocks = [Mock() for _ in range(10)]
    detector._listeners_connected = [listener_mock.listener for listener_mock in connected_mocks]

    disconnected_mocks = [Mock() for _ in range(10)]
    detector._listeners_disconnected = [listener_mock.listener for listener_mock in disconnected_mocks]

    detector._update()
    assert detector._last_connected_devices == []
    for listener_mock in connected_mocks:
        listener_mock.listener.assert_not_called()
    for listener_mock in disconnected_mocks:
        listener_mock.listener.assert_called()


@mock.patch('client.src.usb_detector.detector._store_connected_devices')
@mock.patch('client.src.usb_detector.detector.read_connected_devices', return_value=[2, 3, 4])
def test_update_1(read_connected_devices_mock, _store_connected_devices_mock):
    detector._last_connected_devices = [1, 2, 3, 5]
    connected_mocks = [Mock() for _ in range(10)]
    detector._listeners_connected = [listener_mock.listener for listener_mock in connected_mocks]

    disconnected_mocks = [Mock() for _ in range(10)]
    detector._listeners_disconnected = [listener_mock.listener for listener_mock in disconnected_mocks]

    detector._update()
    assert detector._last_connected_devices == [2, 3, 4]
    for listener_mock in connected_mocks:
        listener_mock.listener.assert_called()
    for listener_mock in disconnected_mocks:
        listener_mock.listener.assert_called()
