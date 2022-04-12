from sys import exit
from configparser import RawConfigParser


class Config:
    """This class holds the configuration values of the application.

    It reads the configuration file passed in through the constructor
    and stores the values into class variables.
    """

    def __init__(self, filepath):
        """Constructor of the class.

        It instantiates the class, reads the configuration file,
        and parses all sections defined in it.

        :param filepath: path to the configuration file
        """
        # Create a new ConfigParser
        self.config = RawConfigParser()

        # Try to parse the configuration file. If it fails,
        # terminate the application.
        if not self.config.read(filepath):
            print(f"Failed to parse the config file {filepath}. Make sure you entered a valid path.")
            exit(1)

        # Parse the 'usb detector' section.
        self._parse_usb_detector_section()

        # Parse the 'server' section (API).
        self._parse_server_section()

        # Parse the 'logger' section.
        self._parse_logger_section()

        # Parse the 'cache' section.
        self._parse_cache_section()

    def _parse_usb_detector_section(self):
        """Parse the 'usb detector' section of the configuration file.
        """
        section_name = "usb_detector"
        self.scan_period_seconds = float(self.config[section_name]["scan_period_seconds"])
        self.connected_devices_filename = self.config[section_name]["connected_devices_filename"]

    def _parse_server_section(self):
        """Parse the 'server' section of the configuration file.
        """
        section_name = "server"
        self.server_url = self.config[section_name]["url"]
        self.server_port = self.config[section_name]["port"]
        self.server_endpoint = self.config[section_name]["end_point"]

    def _parse_logger_section(self):
        """Parse the 'logger' section of the configuration file.
        """
        section_name = "logger"
        self.logger_config_file = self.config[section_name]["config_file"]

    def _parse_cache_section(self):
        """Parse the 'cache' section of the configuration file.
        """
        section_name = "cache"
        self.cache_dir = self.config[section_name]["directory"]
        self.cache_max_entries = int(self.config[section_name]["max_entries"])
        self.cache_max_retries = int(self.config[section_name]["max_retries"])
        self.cache_retry_period_seconds = float(self.config[section_name]["retry_period_seconds"])
