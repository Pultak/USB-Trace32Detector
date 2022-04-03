import logging
import logging.config
from os.path import exists
from threading import Thread
from tendo import singleton
from sys import exit

from config_manager import Config
from usb_detector.detector import register_listener, usb_detector_run, usb_detector_set_config
from usb_detector.event_listener import usb_connected_callback, usb_disconnected_callback
from api_client import api_client_run, api_client_set_config


def init_logging(app_config: Config):
    if exists(app_config.logger_config_file):
        logging.config.fileConfig(fname=app_config.logger_config_file)
        api_client_set_config(app_config)
        usb_detector_set_config(app_config)
    else:
        print(f"Cannot find logger configuration \"{app_config.logger_config_file}\"! Please specify valid a path or define a new one.")
        exit(1)


if __name__ == "__main__":
    try:
        app_instance = singleton.SingleInstance()
    except singleton.SingleInstanceException:
        exit(1)

    config = Config("config.ini")
    init_logging(config)

    register_listener(callback=usb_connected_callback, connected=True)
    register_listener(callback=usb_disconnected_callback, connected=False)

    usb_detector_thread = Thread(target=usb_detector_run)
    usb_detector_thread.setDaemon(True)

    api_thread = Thread(target=api_client_run)
    api_thread.setDaemon(True)

    logging.info("Starting USB detector.")
    usb_detector_thread.start()

    logging.info("Starting API communication manager.")
    api_thread.start()

    usb_detector_thread.join()
    api_thread.join()
