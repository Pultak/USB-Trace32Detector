from configparser import RawConfigParser


CONFIG_FILE = "config.ini"

usb_detector_section = "usb_detector"
server_section = "server"
logger_section = "logger"
cache_section = "cache"

config = RawConfigParser()
config.read(CONFIG_FILE)

scan_period_seconds = float(config[usb_detector_section]["scan_period_seconds"])
connected_devices_filename = config[usb_detector_section]["connected_devices_filename"]

server_url = config[server_section]["url"]
server_port = config[server_section]["port"]
server_endpoint = config[server_section]["end_point"]

logger_format = config[logger_section]["format"]
logger_level_str = config[logger_section]["level"]
logger_level = 0

if logger_level_str == "DEBUG":
    logger_level = 10
elif logger_level_str == "INFO":
    logger_level = 20
elif logger_level_str == "WARNING":
    logger_level = 30
elif logger_level_str == "ERROR":
    logger_level = 40
elif logger_level_str == "CRITICAL":
    logger_level = 50
