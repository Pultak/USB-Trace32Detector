import platform
import logging
import getpass
from datetime import datetime


def _get_metadata() -> dict:
    return {
        "username": getpass.getuser(),
        "hostname": platform.uname().node,
        "timestamp": str(datetime.now())
    }


def _send_payload_to_server(device: dict, status: str):
    payload = _get_metadata()
    payload["device"] = device
    payload["status"] = status

    # TODO send the payload off to the server


def usb_connected_callback(device: dict):
    logging.info(f"Device {device} has been connected")
    _send_payload_to_server(device, "connected")


def usb_disconnected_callback(device: dict):
    logging.info(f"Device {device} has been disconnected")
    _send_payload_to_server(device, "disconnected")
