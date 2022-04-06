from client.src.usb_detector import detector


def test_register_listener_1():
    def connected_handler():
        pass

    detector.register_listener(connected_handler)

    assert connected_handler in detector._listeners_connected
    assert connected_handler not in detector._listeners_disconnected


def test_register_listener_2():
    def connected_handler():
        pass

    detector.register_listener(connected_handler, connected=True)

    assert connected_handler in detector._listeners_connected
    assert connected_handler not in detector._listeners_disconnected


def test_register_listener_3():
    def connected_handler():
        pass

    detector.register_listener(connected_handler, connected=False)

    assert connected_handler in detector._listeners_disconnected
    assert connected_handler not in detector._listeners_connected
