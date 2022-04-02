import logging

import usb.core
import usb.util


_invalid_devices = []


def read_connected_devices():
    logging.debug("reading all currently connected devices")
    detected_devices = []

    busses = usb.busses()

    for bus in busses:
        devices = bus.devices
        for dev in devices:
            device = {
                "vendor_id": dev.idVendor,
                "product_id": dev.idProduct
            }
            serial_number = None
            device_info = usb.core.find(idProduct=dev.idProduct)
            try:
                serial_number = usb.util.get_string(device_info, device_info.iSerialNumber)
            except:
                if device not in _invalid_devices:
                    logging.warning(f"Could not retrieve serial number from device {device}")
                    _invalid_devices.append(device)

            if serial_number is not None:
                if device in _invalid_devices:
                    _invalid_devices.remove(device)

                device["serial_number"] = serial_number
                detected_devices.append(device)

    return detected_devices
