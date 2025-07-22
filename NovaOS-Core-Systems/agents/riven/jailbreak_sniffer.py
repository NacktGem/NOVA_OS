

"""
Riven Agent — Jailbreak Sniffer
Detects signs of OS jailbreaks, rootkits, and privilege escalation on macOS, Linux, and Android systems.
"""

import os
import subprocess
import platform
from datetime import datetime
from config.audit_logger import log_event

def is_root_user():
    return os.geteuid() == 0 if hasattr(os, "geteuid") else False

def check_suspicious_paths(paths):
    return [path for path in paths if os.path.exists(path)]

def scan_mac():
    red_flags = check_suspicious_paths([
        "/Applications/Cydia.app",
        "/Library/MobileSubstrate/MobileSubstrate.dylib",
        "/bin/bash",  # shouldn't be modified
        "/etc/apt",
        "/private/var/lib/apt/",
        "/private/var/stash"
    ])

    try:
        output = subprocess.check_output(["csrutil", "status"], stderr=subprocess.DEVNULL).decode()
        if "disabled" in output.lower():
            red_flags.append("System Integrity Protection is disabled")
    except:
        red_flags.append("Unable to verify System Integrity Protection")

    return red_flags

def scan_linux():
    red_flags = check_suspicious_paths([
        "/usr/sbin/sshd",
        "/etc/ssh/sshd_config",
        "/usr/bin/sudo",
        "/usr/bin/su",
        "/etc/init.d/rcS",
        "/sbin/su"
    ])

    try:
        with open("/proc/sys/kernel/randomize_va_space") as f:
            if f.read().strip() == "0":
                red_flags.append("ASLR is disabled")
    except:
        red_flags.append("Unable to verify ASLR status")

    return red_flags

def scan_android():
    red_flags = check_suspicious_paths([
        "/system/app/Superuser.apk",
        "/sbin/su",
        "/system/bin/su",
        "/system/xbin/su",
        "/data/local/xbin/su",
        "/data/local/bin/su",
        "/system/sd/xbin/su",
        "/system/bin/failsafe/su",
        "/data/local/su"
    ])

    try:
        output = subprocess.check_output(["getprop", "ro.build.tags"], stderr=subprocess.DEVNULL).decode()
        if "test-keys" in output:
            red_flags.append("Build tags contain 'test-keys'")
    except:
        red_flags.append("Unable to verify build tags")

    return red_flags

def run_jailbreak_scan():
    os_type = platform.system()
    results = []

    if os_type == "Darwin":
        results = scan_mac()
    elif os_type == "Linux":
        if "ANDROID_ROOT" in os.environ:
            results = scan_android()
        else:
            results = scan_linux()
    else:
        results.append("Unsupported platform")

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "platform": os_type,
        "root_user": is_root_user(),
        "alerts": results
    }

    log_event("jailbreak_scan", report)
    return report

if __name__ == "__main__":
    print(run_jailbreak_scan())