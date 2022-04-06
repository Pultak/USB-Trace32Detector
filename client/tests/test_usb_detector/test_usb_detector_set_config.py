from client.src.usb_detector import detector


def test_usb_detector_set_config_1():
    assert None is detector._config


def test_usb_detector_set_config_2():
    class Config:
        pass

    config = Config()
    detector.usb_detector_set_config(config)
    assert config is detector._config
