import os
import json
import logging
from time import sleep

from .usb_reader import read_connected_devices
from config_manager import scan_period_seconds, connected_devices_filename


_listeners_connected = []
_listeners_disconnected = []


def register_listener(callback, connected: bool = True):
    if connected is True:
        _listeners_connected.append(callback)
    else:
        _listeners_disconnected.append(callback)


def _notify_listeners(listeners: list, devices: list):
    for callback in listeners:
        for device in devices:
            callback(device)


def _store_connected_devices(devices: list):
    with open(connected_devices_filename, "w") as file:
        json.dump(devices, file)


def _load_last_connected_devices() -> list:
    try:
        with open(connected_devices_filename, "r") as file:
            return json.loads(file.read())
    except IOError:
        return []


def usb_detector_run():
    logging.info("USB device detector is now running")

    if not os.path.exists(connected_devices_filename):
        dir_name = os.path.dirname(connected_devices_filename)
        os.makedirs(dir_name)

    while True:
        last_connected_devices = _load_last_connected_devices()
        detected_devices = read_connected_devices()

        connected_devices = [device for device in detected_devices if device not in last_connected_devices]
        disconnected_devices = [device for device in last_connected_devices if device not in detected_devices]

        _notify_listeners(_listeners_connected, connected_devices)
        _notify_listeners(_listeners_disconnected, disconnected_devices)

        _store_connected_devices(detected_devices)
        sleep(scan_period_seconds)
