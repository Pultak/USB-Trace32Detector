import usb.core
import usb.util


def read_connected_devices():
    detected_devices = []

    busses = usb.busses()

    for bus in busses:
        devices = bus.devices
        for dev in devices:
            detected_devices.append({
                "vendor_id": dev.idVendor,
                "product_id": dev.idProduct
            })

    return detected_devices
