from client.src.usb_detector.usb_reader import read_connected_devices


def test_read_connected_devices_1():
    # This test assumes that there is no USB plugged in.
    assert read_connected_devices() == []
