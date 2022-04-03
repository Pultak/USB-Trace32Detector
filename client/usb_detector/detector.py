import json
import logging
from time import sleep

from .usb_reader import read_connected_devices


_listeners_connected = []
_listeners_disconnected = []
_last_connected_devices = []
_config = None


def usb_detector_set_config(config):
    global _config
    _config = config


def register_listener(callback, connected: bool = True):
    logging.info(f"Registering callback: {callback}.")
    if connected is True:
        _listeners_connected.append(callback)
    else:
        _listeners_disconnected.append(callback)


def _notify_listeners(listeners: list, devices: list):
    if listeners is None or devices is None:
        return
    for callback in listeners:
        for device in devices:
            callback(device)


def _store_connected_devices(devices: list):
    logging.debug("storing newly connected devices")
    with open(_config.connected_devices_filename, "w") as file:
        json.dump(devices, file)


def _load_last_connected_devices() -> list:
    logging.debug("loading last connected devices")
    try:
        with open(_config.connected_devices_filename, "r") as file:
            return json.loads(file.read())
    except IOError:
        logging.error("loading of last connected devices failed")
        return []


def _get_connected_devices(detected_devices: list, last_connected_devices: list) -> list:
    return [device for device in detected_devices if device not in last_connected_devices]


def _get_disconnected_devices(detected_devices: list, last_connected_devices: list) -> list:
    return [device for device in last_connected_devices if device not in detected_devices]


def _update():
    global _last_connected_devices
    detected_devices = read_connected_devices()

    connected_devices = _get_connected_devices(detected_devices, _last_connected_devices)
    disconnected_devices = _get_disconnected_devices(detected_devices, _last_connected_devices)

    _notify_listeners(_listeners_connected, connected_devices)
    _notify_listeners(_listeners_disconnected, disconnected_devices)

    if len(connected_devices) > 0 or len(disconnected_devices) > 0:
        _store_connected_devices(detected_devices)
        _last_connected_devices = detected_devices


def usb_detector_run():
    logging.info("USB device detector is now running")

    global _last_connected_devices
    _last_connected_devices = _load_last_connected_devices()

    while True:
        _update()
        sleep(_config.scan_period_seconds)
