import json
import logging
from time import sleep

_listeners_connected = []       # list of listeners (USB devices is connected)
_listeners_disconnected = []    # list of listeners (USB devices is disconnected)

_last_connected_devices = []    # list of the lastly connected USB devices
_config = None                  # instance of Config (config manager)
_usb_reader = None


def usb_detector_set_config(config, usbReader):
    """Initializes the usb detector module (file).

    This function is meant to be called prior to calling
    any other function of the detector module. It stores
    an instance of the Config class which is then used
    by other functions within this file.

    :param usbReader: .]
    :param config: instance of Config (config manager)
    """
    # Store the instance into the global variable.
    global _config, _usb_reader
    _config = config
    _usb_reader = usbReader


def register_listener(callback, connected: bool = True):
    """Registers a new event listener.

    The caller is supposed to pass in a function they
    wish to be called whenever an event occurs. What kind
    of event will trigger (call) the callback function is
    determined by the second parameter.

    :param callback: Function that is called whenever the desired event happens.
    :param connected: If the value is set to True, the callback function
                      will be called whenever a USB device is connected.
                      If it is set to False, it will be triggered whenever a
                      USB device is disconnected.
    """
    logging.info(f"Registering callback: {callback}.")

    if connected is True:
        # Register the callback for "connected devices"
        _listeners_connected.append(callback)
    else:
        # Register the callback for "disconnected devices"
        _listeners_disconnected.append(callback)


def _notify_listeners(listeners: list, devices: list):
    """ Notifies (calls) all listeners based on the even that just occurred.

    This function is called whenever a USB device is plugged or unplugged.
    Based on the type of the event, the corresponding list of listeners
    is passed in along with a list of all devices involved in the event.

    :param listeners: list of listeners registered for the event
    :param devices: list of all USB devices involved in the event
                    (usually a single device)
    """
    # Make sure both lists are not None.
    if listeners is None or devices is None:
        return

    # Iterate over the listeners and notify them
    # of all USB devices involved in the event.
    for callback in listeners:
        for device in devices:
            callback(device)


def _store_connected_devices(devices: list):
    """Stores the list of the currently connected USB devices into a file.

    This function is called whenever a device is connected or disconnected.
    Its main purpose is to dump the list of the currently plugged devices
    on the disk (so it is not kept in RAM when the computer shuts down). The
    list is then loaded upon every start of the application.

    :param devices: list of the devices that are currently connected to the PC
    """
    logging.debug("storing newly connected devices")

    # Dump the list into a JSON format.
    with open(_config.connected_devices_filename, "w") as file:
        json.dump(devices, file)


def _load_last_connected_devices() -> list:
    """Loads the list of the connected devices from the disk.

    This function is called with every start of the application.
    It ensures that the application remembers the USB devices
    that were connected to the PC before it was turned off
    (persistent memory).

    :return: list of the lastly connected USB devices
    """
    logging.debug("loading last connected devices")
    try:
        with open(_config.connected_devices_filename, "r") as file:
            return json.loads(file.read())
    except IOError:
        logging.error("loading of last connected devices failed")
        return []


def _get_connected_devices(detected_devices: list, last_connected_devices: list) -> list:
    """Returns a list of USB devices that were just plugged into the computer.

    Using the two lists passed in as parameters, it figures out what devices
    were just connected to the PC. Essentially, any device in the detected_devices list
    that does not apper in the last_connected_devices list must have been just plugged in.

    :param detected_devices: list of the currently plugged USB devices
    :param last_connected_devices: list of the lastly connected USB devices
    :return: list of all USB devices that were just plugged into the computer
    """
    # If there is no previous record of what USB devices where connected to the PC,
    # all newly-connected devices are treated as if they were just plugged in.
    if last_connected_devices is None and detected_devices is not None:
        return detected_devices

    # Return an empty list if no devices were detected.
    if detected_devices is None:
        return []

    # Return a list of all devices that were just plugged into the PC.
    return [device for device in detected_devices if device not in last_connected_devices]


def _get_disconnected_devices(detected_devices: list, last_connected_devices: list) -> list:
    """Returns a list of USB devices that were just disconnected from the computer.

    Using the two lists passed in as parameters, it figures out what devices where just
    disconnected from the computer. Basically, any device that was seen connected to the PC
    and does not apper in the detected_devices list must have been just unplugged from the PC.

    :param detected_devices: list of the currently plugged USB devices
    :param last_connected_devices: list of the lastly connected USB devices
    :return: list of all USB devices that were just disconnected from the PC
    """
    # If there is no previous record of what USB devices where connected to the PC,
    # no devices were unplugged
    if last_connected_devices is None:
        return []

    # Return last_connected_devices if no devices were detected.
    if detected_devices is None:
        return last_connected_devices

    # Return a list of all devices that were just disconnected.
    return [device for device in last_connected_devices if device not in detected_devices]


def _update():
    """Updates the USB detector.

    This function is periodically called from the usb_detector_run function.
    It uses the other functions of this file to figure out if there have
    been any changes since the last time this function was called - what
    USB devices have been connected/disconnected.
    """
    # Retrieve a list of the currently plugged USB devices
    # and store it globally within the file.
    global _last_connected_devices
    detected_devices = _usb_reader.read_connected_devices_power_shell()

    # Figure out what USB devices were connected to the PC since
    # the last time this function was called.
    connected_devices = _get_connected_devices(detected_devices, _last_connected_devices)

    # Figure out what USB devices were disconnected from the PC since
    # the last time this function was called.
    disconnected_devices = _get_disconnected_devices(detected_devices, _last_connected_devices)

    # Notify both kinds of listeners (call the registered callback functions).
    _notify_listeners(_listeners_connected, connected_devices)
    _notify_listeners(_listeners_disconnected, disconnected_devices)

    # If there have been any changes, update the file on the disk (persistent memory).
    if len(connected_devices) > 0 or len(disconnected_devices) > 0:
        _store_connected_devices(detected_devices)
        _last_connected_devices = detected_devices


def usb_detector_run():
    """Keeps detecting what USB devices were plugged/unplugged.

    This function is instantiated as a thread that periodically scans
    what USB devices are connected to the PC. The scan period can be
    found and modified in the configuration file of the application.
    """
    logging.info("USB device detector is now running")

    # Read the list of the lastly connected USB devices from the disk (once).
    global _last_connected_devices
    _last_connected_devices = _load_last_connected_devices()

    while True:
        # Update the USB detector.
        _update()

        # Sleep for a predefined amount of seconds.
        sleep(_config.scan_period_seconds)
