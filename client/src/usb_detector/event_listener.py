import platform
import logging
import getpass
from datetime import datetime

from .api_client import send_data


def _get_metadata() -> dict:
    """Returns metadata associated with the computer.

    This metadata is sent to the server as a part
    of each payload. It includes the username, hostname,
    and timestamp.

    :return: metadata associated with the PC
    """
    logging.debug("getting computer metadata")
    return {
        "username": getpass.getuser(),                  # username
        "hostname": platform.uname().node,              # hostname
        "timestamp": str(datetime.now()).split('.')[0]  # timestamp (format: 2022-04-07 12:11:02)
    }


def _send_payload_to_server(device: dict, status: str):
    """ Creates a payload and calls the send_data function to send it to the server.

    Each payload consists of metadata, status (connected/disconnected), and device,
    which contains a vendor id, product id, and serial number.

    :param device: USB device that has been detected
    :param status: status of the USB device (connected/disconnected)
    """
    logging.debug("payload send preparation")

    # Get metadata that will be put into the payload.
    payload = _get_metadata()

    # Add information about the USB device.
    payload["device"] = device

    # Add the status of the USB device (connected/disconnected).
    payload["status"] = status

    # Send the payload off to the server.
    send_data(payload)


def usb_connected_callback(device: dict):
    """Callback function for a connected USB device.

    This function gets called whenever a USB device is
    plugged into the computer (it is registered as a listener in
    the USB detector). The device consists of a vendor id, product id,
    and serial number.

    :param device: USB device that was just plugged into the PC.
    """
    logging.info(f"Device {device} has been connected")

    # Create a payload and send it to the API (server).
    _send_payload_to_server(device, "connected")


def usb_disconnected_callback(device: dict):
    """Callback function for a disconnected USB device.

    This function gets called whenever a USB device is
    disconnected from the computer (it is registered as a listener in
    the USB detector). The device consists of a vendor id, product id,
    and serial number.

    :param device: USB device that was just disconnected from the PC.
    """
    logging.info(f"Device {device} has been disconnected")

    # Create a payload and send it to the API (server).
    _send_payload_to_server(device, "disconnected")
