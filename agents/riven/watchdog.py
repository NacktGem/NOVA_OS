

"""
Riven Agent — Surveillance Watchdog
Monitors key system files and directories for tampering, unauthorized access, or privilege escalations.
"""

import os
import time
import hashlib
import platform
from datetime import datetime
from config.audit_logger import log_event

WATCH_PATHS = [
    "/etc/passwd",
    "/etc/shadow",
    "/etc/sudoers",
    "/bin/bash",
    "/usr/bin/python3",
    "/Library/Preferences/SystemConfiguration",  # macOS network config
]

CHECK_INTERVAL = 60  # seconds

def get_file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None

def snapshot_files(paths):
    return {p: get_file_hash(p) for p in paths if os.path.exists(p)}

def detect_changes(before, after):
    changes = []
    for path in before:
        if before[path] != after.get(path):
            changes.append({
                "file": path,
                "old_hash": before[path],
                "new_hash": after.get(path),
                "timestamp": datetime.utcnow().isoformat()
            })
    return changes

def run_watchdog_loop():
    os_type = platform.system()
    initial_snapshot = snapshot_files(WATCH_PATHS)
    time.sleep(CHECK_INTERVAL)

    while True:
        current_snapshot = snapshot_files(WATCH_PATHS)
        modified = detect_changes(initial_snapshot, current_snapshot)

        if modified:
            for change in modified:
                log_event("watchdog_alert", {
                    "platform": os_type,
                    "file": change["file"],
                    "old_hash": change["old_hash"],
                    "new_hash": change["new_hash"],
                    "timestamp": change["timestamp"]
                })

        initial_snapshot = current_snapshot
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_watchdog_loop()