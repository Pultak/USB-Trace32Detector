import logging

import subprocess
import json
import re

MAX_ATTEMPT_COUNT = 1000


class UsbReader:

    def __init__(self, config):
        self.powershell_process = subprocess.Popen(["powershell.exe"],
                                                   stdout=subprocess.PIPE,
                                                   stdin=subprocess.PIPE,
                                                   stderr=subprocess.PIPE,
                                                   startupinfo=None)
        self.pnp_command = b"Get-PnpDevice -Class 'HIDClass' -Status 'OK' |" \
                           b" Select-Object InstanceId | ConvertTo-Json\n"
        self.config = config
        # list of devices from which the application
        # could not retrieve a serial number
        self._invalid_devices = []

    def __exit__(self, exc_type, exc_value, traceback):
        self.powershell_process.stdin.close()
        self.powershell_process.stdout.close()

#    def read_connected_devices(self):
        """Reads and returns all USB devices that are currently connected to the computer.

        It iterates over devices connected to individual buses and for each of
        them, it tries to retrieve its vendor id, product id, and serial number.
        If the application fails to retrieve the serial number of a device, it
        will store it into an in-RAM list to prevent "spam" logs. Once the application
        manages to read the serial number, the device will be removed from the list.

        :return: list of all USB devices connected to the PC
        """
        #        logging.debug("reading all currently connected devices")

        # Create an empty list of USB devices.
        #       detected_devices = []

        # Get a list of all buses.
        #     busses = usb.busses()

        #    for bus in busses:
            # Get all devices connected to the current bus.
        #      devices = bus.devices
        #     for dev in devices:
                # Create a record of the device.
        #         device = {
        #           "vendor_id": dev.idVendor,
        #            "product_id": dev.idProduct
        #        }

                # Try to retrieve the serial number of the device.
        #        serial_number = None
        #        device_info = usb.core.find(idProduct=dev.idProduct)
        #        try:
        #             serial_number = usb.util.get_string(device_info, device_info.iSerialNumber)
        #        except ValueError:
                    # If you fail, store the device into the in-RAM list (if it is not already there).
        #           if device not in self._invalid_devices:
        #                logging.warning(f"Could not retrieve serial number from device {device}")
        #                self._invalid_devices.append(device)

        #       if serial_number is not None:
                    # If you manage to read the serial number of a USB device
                    # that was previously stored into the list of "failures", remove it.
        #           if device in self._invalid_devices:
        #               self._invalid_devices.remove(device)

                    # Add the serial number into to USB device record.
        #           device["serial_number"] = serial_number

                    # Append the record into the list of the connected USB devices.
        #           detected_devices.append(device)

        # Return the list of currently plugged USB devices.
        # return detected_devices

    def read_connected_devices_power_shell(self):
        """Reads and returns all USB devices that are currently connected to the computer.

        It iterates over devices detected by powershell Get-PnpDevice command
        and for each of them, it tries to retrieve its vendor id, product id, and serial number.
        If the application fails to retrieve the serial number of a device, it
        will store it into an in-RAM list to prevent "spam" logs. Once the application
        manages to read the serial number, the device will be removed from the list.

        :return: list of all USB devices connected to the PC
        """
        logging.debug("reading all currently connected devices")

        # Create an empty list of USB devices.
        detected_devices = []
        self.powershell_process.stdin.write(self.pnp_command)
        self.powershell_process.stdin.flush()

        out = self.read_json_input()

        json_devices = json.loads(out)
        for json_device in json_devices:
            for id_suffix in self.config.pnp_device_id_suffixes:
                if id_suffix in json_device['InstanceId']:
                    detected_device = {}
                    try:
                        detected_device['vendor_id'] = re.search("(?<=VID_)[\\d\\w]+", json_device['InstanceId']).group(0)
                        detected_device['product_id'] = pid = re.search("(?<=PID_)[\\d\\w]+",
                                                                        json_device['InstanceId']).group(0)
                        detected_device['serial_number'] = re.search("(?<=PID_" + pid + "\\\\)[\\d\\w]+",
                                                                     json_device['InstanceId']).group(0)

                        if detected_device in self._invalid_devices:
                            self._invalid_devices.remove(detected_device)

                        # Append the record into the list of the connected USB devices.
                        detected_devices.append(detected_device)
                    except ValueError:
                        # If you fail, store the device into the in-RAM list (if it is not already there).
                        logging.warning(f"Could not retrieve serial number from device {json_device}")

        # Return the list of currently plugged USB devices.
        return detected_devices

    def read_json_input(self):

        last_char = ''
        attempt = 0
        result = b""
        inside_json_array = False

        while attempt < MAX_ATTEMPT_COUNT:
            last_char = self.powershell_process.stdout.read(1)
            if b'[' == last_char:
                inside_json_array = True
                result += last_char
                break
            attempt += 1
        if inside_json_array:
            while last_char != b']':
                last_char = self.powershell_process.stdout.read(1)
                result += last_char
            return result
        else:
            logging.error("Message output from the powershell is in invalid format! Please check the output of the "
                          "powershell process")
            return None
