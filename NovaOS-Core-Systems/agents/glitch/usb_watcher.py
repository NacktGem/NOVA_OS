

"""
Glitch Agent — USB Watcher
Detects real-time USB device insertions/removals using macOS IOKit APIs and triggers forensic logging.
"""

import subprocess
import time
import json
from datetime import datetime
from config.audit_logger import log_event

POLL_INTERVAL = 5  # seconds
LAST_STATE = set()


def get_connected_usb_devices():
    """
    Uses system_profiler to query USB device tree.

    Returns:
        set: A set of connected device identifiers (e.g. vendor + product ID).
    """
    try:
        output = subprocess.check_output(["system_profiler", "SPUSBDataType", "-json"], stderr=subprocess.DEVNULL)
        data = json.loads(output)
        devices = extract_device_ids(data.get("SPUSBDataType", []))
        return devices
    except Exception as e:
        log_event("usb_scan_error", {"error": str(e), "timestamp": datetime.utcnow().isoformat()})
        return set()


def extract_device_ids(tree, parent="Root Hub"):
    """
    Recursively extract USB device identifiers from system profiler tree.

    Args:
        tree (list): Parsed JSON data from system_profiler.

    Returns:
        set: Device identifiers.
    """
    ids = set()
    for node in tree:
        name = node.get("_name", "Unknown Device")
        vendor_id = node.get("vendor_id", "N/A")
        product_id = node.get("product_id", "N/A")
        device_str = f"{name}_{vendor_id}_{product_id}"
        ids.add(device_str)

        if "._items" in node:
            ids |= extract_device_ids(node["._items"], parent=name)

    return ids


def monitor_usb():
    global LAST_STATE
    while True:
        current_state = get_connected_usb_devices()
        inserted = current_state - LAST_STATE
        removed = LAST_STATE - current_state

        for device in inserted:
            log_event("usb_inserted", {
                "device_id": device,
                "timestamp": datetime.utcnow().isoformat()
            })

        for device in removed:
            log_event("usb_removed", {
                "device_id": device,
                "timestamp": datetime.utcnow().isoformat()
            })

        LAST_STATE = current_state
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    log_event("usb_monitor_start", {"timestamp": datetime.utcnow().isoformat()})
    monitor_usb()