from client.src.usb_detector import detector


def test_get_connected_devices_1():
    assert detector._get_connected_devices([], []) == []


def test_get_connected_devices_2():
    assert detector._get_connected_devices([], None) == []


def test_get_connected_devices_3():
    assert detector._get_connected_devices(None, []) == []


def test_get_connected_devices_4():
    assert detector._get_connected_devices(None, None) == []


def test_get_connected_devices_5():
    assert detector._get_connected_devices([1, 2, 3], None) == [1, 2, 3]


def test_get_connected_devices_6():
    assert detector._get_connected_devices(None, [4, 5, 6]) == []


def test_get_connected_devices_7():
    assert detector._get_connected_devices([], [4, 5, 6]) == []


def test_get_connected_devices_8():
    assert detector._get_connected_devices([1, 2, 3], []) == [1, 2, 3]


def test_get_connected_devices_9():
    assert detector._get_connected_devices([1, 2, 3], [2, 3]) == [1]


def test_get_connected_devices_10():
    detected_devices = [
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
    last_connected_devices = [
        {
            "vendor_id": 1,
            "product_id": 2,
            "serial_number": 3
        }
    ]
    assert detector._get_connected_devices(detected_devices, last_connected_devices) == [detected_devices[1]]
    assert detector._get_connected_devices(detected_devices, None) == detected_devices
    assert detector._get_connected_devices(detected_devices, []) == detected_devices
