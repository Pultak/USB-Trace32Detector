import logging
from threading import Thread
from tendo import singleton

from config_manager import logger_format, logger_level
from usb_detector.detector import register_listener, usb_detector_run
from usb_detector.event_listener import usb_connected_callback, usb_disconnected_callback
from api_client import api_client_run


if __name__ == "__main__":
    app_instance = singleton.SingleInstance()

    logging.basicConfig(format=logger_format, level=logger_level)

    register_listener(callback=usb_connected_callback, connected=True)
    register_listener(callback=usb_disconnected_callback, connected=False)

    usb_detector_thread = Thread(target=usb_detector_run)
    usb_detector_thread.setDaemon(True)

    api_thread = Thread(target=api_client_run)
    api_thread.setDaemon(True)

    usb_detector_thread.start()
    api_thread.start()

    usb_detector_thread.join()
    api_thread.join()
