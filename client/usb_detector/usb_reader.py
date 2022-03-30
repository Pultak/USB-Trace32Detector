import logging

import usb.core
import usb.util


def read_connected_devices():
    logging.debug(f'reading all currently connected devices')
    detected_devices = []

    busses = usb.busses()

    for bus in busses:
        devices = bus.devices
        for dev in devices:
            serial_number = None
            device_info = usb.core.find(idProduct=dev.idProduct)
            try:
                serial_number = usb.util.get_string(device_info, device_info.iSerialNumber)
            except:
                # Failed to retrieve information from device
                logging.info(f"device idVendor:{dev.idVendor} idProduct:{dev.idProduct} has invalid format")
                pass

            if serial_number is not None:
                detected_devices.append({
                    "vendor_id": dev.idVendor,
                    "product_id": dev.idProduct,
                    "serial_number": serial_number
                })

    return detected_devices
