from unittest.mock import Mock

from client.src.usb_detector import detector


def test_notify_listeners_1():
    mocks = [Mock() for _ in range(10)]
    detector._notify_listeners([mock.listener for mock in mocks], [1, 2, 3])
    for mock in mocks:
        mock.listener.assert_called()


def test_notify_listeners_2():
    mocks = [Mock() for _ in range(10)]
    detector._notify_listeners([mock.listener for mock in mocks], [])
    for mock in mocks:
        mock.listener.assert_not_called()


def test_notify_listeners_3():
    mocks = [Mock() for _ in range(10)]
    detector._notify_listeners([mock.listener for mock in mocks], None)
    for mock in mocks:
        mock.listener.assert_not_called()
