import getpass
import platform
from datetime import datetime

from client.src.usb_detector import event_listener


def test_get_metadata_1():
    expected_metadata = {
        "username": getpass.getuser(),
        "hostname": platform.uname().node,
        "timestamp": str(datetime.now()).split('.')[0]
    }

    actual_metadata = event_listener._get_metadata()

    assert actual_metadata["username"] == expected_metadata["username"]
    assert actual_metadata["hostname"] == expected_metadata["hostname"]
    assert actual_metadata["timestamp"] == expected_metadata["timestamp"]
