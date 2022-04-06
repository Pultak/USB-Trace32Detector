from client.src.usb_detector import detector


def test_get_disconnected_devices_1():
    assert detector._get_disconnected_devices([], []) == []


def test_get_disconnected_devices_2():
    assert detector._get_disconnected_devices([], None) == []


def test_get_disconnected_devices_3():
    assert detector._get_disconnected_devices(None, []) == []


def test_get_disconnected_devices_4():
    assert detector._get_disconnected_devices(None, None) == []


def test_get_disconnected_devices_5():
    assert detector._get_disconnected_devices([1, 2, 3, 4, 5], None) == []


def test_get_disconnected_devices_6():
    assert detector._get_disconnected_devices([1, 2, 3, 4, 5], []) == []


def test_get_disconnected_devices_7():
    assert detector._get_disconnected_devices([1, 3, 5], [1, 2, 3, 4, 5]) == [2, 4]


def test_get_disconnected_devices_8():
    assert detector._get_disconnected_devices([], [1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]


def test_get_disconnected_devices_9():
    assert detector._get_disconnected_devices([], [1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]


def test_get_disconnected_devices_10():
    last_connected_devices = [
        {
            "vendor_id": 1,
            "product_id": 2,
            "serial_number": 3
        },
        {
            "vendor_id": 4,
            "product_id": 5,
            "serial_number": 5
        }
    ]
    detected_devices = [
        {
            "vendor_id": 1,
            "product_id": 2,
            "serial_number": 3
        }
    ]
    assert detector._get_disconnected_devices(detected_devices, last_connected_devices) == [last_connected_devices[1]]
    assert detector._get_disconnected_devices(detected_devices, None) == []
    assert detector._get_disconnected_devices(detected_devices, []) == []
    assert detector._get_disconnected_devices([], last_connected_devices) == last_connected_devices
    assert detector._get_disconnected_devices(None, last_connected_devices) == last_connected_devices


