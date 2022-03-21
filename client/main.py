import logging

from tendo import singleton

from config_manager import logger_format, logger_level

if __name__ == "__main__":
    app_instance = singleton.SingleInstance()

    logging.basicConfig(format=logger_format, level=logger_level)


