import logging

import usb.core
import usb.util


def read_connected_devices():
    detected_devices = []

    busses = usb.busses()

    for bus in busses:
        devices = bus.devices
        for dev in devices:
            try:
                device_info = usb.core.find(idProduct=dev.idProduct)
                detected_devices.append({
                    "vendor_id": dev.idVendor,
                    "product_id": dev.idProduct,
                    "serial_number": usb.util.get_string(device_info, device_info.iSerialNumber)
                })
            except:
                logging.warning(f"Failed to retrieve information from device {dev}")

    return detected_devices
