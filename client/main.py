import logging
import logging.config
from os.path import exists
from threading import Thread
from tendo import singleton

from config_manager import logger_format, logger_level, logger_config
from usb_detector.detector import register_listener, usb_detector_run
from usb_detector.event_listener import usb_connected_callback, usb_disconnected_callback
from api_client import api_client_run

def init_logging():
    if exists(logger_config):
        logging.config.fileConfig(fname=logger_config)
    else:
        print(f"Cant find logger configuration \"{logger_config}\"! Please specify valid path or define new.")
        exit(1)


if __name__ == "__main__":
    app_instance = singleton.SingleInstance()
    init_logging()

    register_listener(callback=usb_connected_callback, connected=True)
    register_listener(callback=usb_disconnected_callback, connected=False)

    usb_detector_thread = Thread(target=usb_detector_run)
    usb_detector_thread.setDaemon(True)

    api_thread = Thread(target=api_client_run)
    api_thread.setDaemon(True)

    logging.info('starting USB detector.')
    usb_detector_thread.start()

    logging.info('starting API communication manager.')
    api_thread.start()

    usb_detector_thread.join()
    api_thread.join()

    logging.info('application exit.')
