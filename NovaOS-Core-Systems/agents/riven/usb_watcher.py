

"""
Riven Agent — USB Surveillance Module
Monitors, fingerprints, and reports USB device activity using macOS APIs for real-time security enforcement.
"""

import subprocess
import time
import json
import hashlib
from datetime import datetime
from config.audit_logger import log_event

POLL_INTERVAL = 5  # seconds
LAST_STATE = set()


def get_connected_usb_devices():
    """
    Extracts USB device metadata using macOS system_profiler.

    Returns:
        set: A set of unique device hash fingerprints.
    """
    try:
        output = subprocess.check_output(["system_profiler", "SPUSBDataType", "-json"], stderr=subprocess.DEVNULL)
        data = json.loads(output)
        devices = extract_device_fingerprints(data.get("SPUSBDataType", []))
        return devices
    except Exception as e:
        log_event("usb_scan_failure", {"error": str(e), "timestamp": datetime.utcnow().isoformat()})
        return set()


def extract_device_fingerprints(tree):
    """
    Recursively scans USB tree and hashes metadata to create device fingerprints.

    Args:
        tree (list): Parsed JSON structure of USB devices.

    Returns:
        set: Fingerprint hashes (SHA-256) of each device.
    """
    fingerprints = set()

    for node in tree:
        device_info = {
            "name": node.get("_name", "Unknown"),
            "manufacturer": node.get("manufacturer", "Unknown"),
            "vendor_id": node.get("vendor_id", "N/A"),
            "product_id": node.get("product_id", "N/A"),
            "serial_number": node.get("serial_num", "N/A"),
            "location_id": node.get("location_id", "N/A")
        }

        # Serialize and hash
        encoded = json.dumps(device_info, sort_keys=True).encode("utf-8")
        device_hash = hashlib.sha256(encoded).hexdigest()
        fingerprints.add(device_hash)

        if "._items" in node:
            fingerprints |= extract_device_fingerprints(node["._items"])

    return fingerprints


def monitor_usb():
    global LAST_STATE
    while True:
        current = get_connected_usb_devices()
        inserted = current - LAST_STATE
        removed = LAST_STATE - current

        for dev_hash in inserted:
            log_event("usb_device_detected", {
                "action": "inserted",
                "fingerprint": dev_hash,
                "timestamp": datetime.utcnow().isoformat()
            })

        for dev_hash in removed:
            log_event("usb_device_removed", {
                "action": "removed",
                "fingerprint": dev_hash,
                "timestamp": datetime.utcnow().isoformat()
            })

        LAST_STATE = current
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    log_event("usb_watcher_started", {"timestamp": datetime.utcnow().isoformat()})
    monitor_usb()