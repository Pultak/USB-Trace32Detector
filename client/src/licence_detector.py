import logging
import logging.config
import argparse
from os.path import exists
from threading import Thread
from tendo import singleton
from sys import exit

from config_manager import Config
from usb_detector.detector import register_listener, usb_detector_run, usb_detector_set_config
from usb_detector.event_listener import usb_connected_callback, usb_disconnected_callback
from usb_detector.api_client import api_client_run, api_client_set_config


def init_logging(app_config: Config):
    """Initializes logging, api client, and usb detector.

    The function checks whether the path to the logger configuration
    file is valid or not. The path is defined in the logger section of the
    main configuration file. It also calls api_client_set_config and
    usb_detector_set_config to fully initialize the application.

    :param app_config: instance of Config (config manager)
    """
    # If the logger configuration file exists.
    if exists(app_config.logger_config_file):
        # Initialize logging according to the logger config file.
        logging.config.fileConfig(fname=app_config.logger_config_file)

        # Initialize the rest of the application.
        api_client_set_config(app_config)
        usb_detector_set_config(app_config)
    else:
        # If the file does not exist, terminate the application.
        print(f"Cannot find logger configuration \"{app_config.logger_config_file}\"! Please specify valid a path or define a new one.")
        exit(1)


if __name__ == "__main__":
    """Main entry point of the application.
    
    The application expects one parameter to be passed in -
    the path to the configuration file. The user can print out help
    using the '-h' option.
    """
    # Make sure that there is only one running instance (process) of this application.
    try:
        app_instance = singleton.SingleInstance()
    except singleton.SingleInstanceException:
        exit(1)

    # Parse the arguments passed in from the command line.
    arg_parser = argparse.ArgumentParser(description="ZF USB License Detector")
    arg_parser.add_argument("-c", "--config", dest="config", required=True, help="Path to the configuration file")
    args = arg_parser.parse_args()

    # Read the configuration file and initialize the application (logging).
    config = Config(args.config)
    init_logging(config)

    # Register callbacks (connected/disconnected USB device).
    register_listener(callback=usb_connected_callback, connected=True)
    register_listener(callback=usb_disconnected_callback, connected=False)

    # Create a thread for the USB detector.
    usb_detector_thread = Thread(target=usb_detector_run)
    usb_detector_thread.setDaemon(True)

    # Create a thread for resending failed payloads to the server.
    api_thread = Thread(target=api_client_run)
    api_thread.setDaemon(True)

    # Start the USB detector thread.
    logging.info("Starting USB detector.")
    usb_detector_thread.start()

    # Start the API client thread.
    logging.info("Starting API communication manager.")
    api_thread.start()

    # The execution should never get here as both
    # threads are infinite loops.
    usb_detector_thread.join()
    api_thread.join()
