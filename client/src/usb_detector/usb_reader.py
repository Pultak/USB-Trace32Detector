import logging

import usb.core
import usb.util


# list of devices from which the application
# could not retrieve a serial number
_invalid_devices = []


def read_connected_devices():
    """Reads and returns all USB devices currently connected to the computer.

    It iterates over devices connected to individual buses and for each of
    them, it tries to retrieve its vendor id, product id, and serial number.
    If the application fails to retrieve the serial number from a device, it
    will be stored into an in-RAM list to prevent "spam" logs. Once the application
    successes to read the serial number, the device will be removed from the list.

    :return: list of all USB devices connected to the PC
    """
    logging.debug("reading all currently connected devices")

    # Create an empty list of USB devices.
    detected_devices = []

    # Get a list of all buses.
    busses = usb.busses()

    for bus in busses:
        # Get all devices connected to the current bus.
        devices = bus.devices
        for dev in devices:
            # Create a record of the device.
            device = {
                "vendor_id": dev.idVendor,
                "product_id": dev.idProduct
            }

            # Try to retrieve the serial number of the device.
            serial_number = None
            device_info = usb.core.find(idProduct=dev.idProduct)
            try:
                serial_number = usb.util.get_string(device_info, device_info.iSerialNumber)
            except ValueError:
                # If you fail, store the device into the in-RAM list (if it's
                # not already there).
                if device not in _invalid_devices:
                    logging.warning(f"Could not retrieve serial number from device {device}")
                    _invalid_devices.append(device)

            if serial_number is not None:
                # If you manage to read the serial number of a USB device
                # that was previously stored into the list of "failures", remove it.
                if device in _invalid_devices:
                    _invalid_devices.remove(device)

                # Add the serial number into to USB device record.
                device["serial_number"] = serial_number

                # Append the record into the list of the connected USB devices.
                detected_devices.append(device)

    # Return the list of currently plugged USB devices.
    return detected_devices
