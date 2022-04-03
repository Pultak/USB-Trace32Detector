import platform
import logging
import getpass
from datetime import datetime

from api_client import send_data


def _get_metadata() -> dict:
    logging.debug("getting computer metadata")
    return {
        "username": getpass.getuser(),
        "hostname": platform.uname().node,
        "timestamp": str(datetime.now())
    }


def _send_payload_to_server(device: dict, status: str):
    logging.debug("payload send preparation")
    payload = _get_metadata()
    payload["device"] = device
    payload["status"] = status
    send_data(payload)


def usb_connected_callback(device: dict):
    logging.info(f"Device {device} has been connected")
    _send_payload_to_server(device, "connected")


def usb_disconnected_callback(device: dict):
    logging.info(f"Device {device} has been disconnected")
    _send_payload_to_server(device, "disconnected")
