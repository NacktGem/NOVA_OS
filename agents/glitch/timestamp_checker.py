

"""
Glitch Agent — Timestamp Checker
Scans file metadata and compares timestamps to detect anomalies, tampering, or forensic red flags.
"""

import os
import time
from pathlib import Path
from typing import Dict
from datetime import datetime
from config.audit_logger import log_event

def analyze_timestamps(file_path: str) -> Dict:
    """
    Inspects access, modification, and creation timestamps of a given file.
    Flags suspicious deltas (e.g. same timestamp, reverse order).

    Args:
        file_path (str): Path to the target file.

    Returns:
        dict: {
            "file": str,
            "created": str,
            "modified": str,
            "accessed": str,
            "delta_created_modified": float,
            "delta_modified_accessed": float,
            "anomaly": str,
            "timestamp": str
        }
    """
    result = {
        "file": file_path,
        "created": "",
        "modified": "",
        "accessed": "",
        "delta_created_modified": 0.0,
        "delta_modified_accessed": 0.0,
        "anomaly": "",
        "timestamp": datetime.utcnow().isoformat()
    }

    path = Path(file_path)
    if not path.exists() or not path.is_file():
        result["anomaly"] = "file_not_found"
        return result

    stat = path.stat()
    created = stat.st_ctime
    modified = stat.st_mtime
    accessed = stat.st_atime

    result["created"] = _ts_to_str(created)
    result["modified"] = _ts_to_str(modified)
    result["accessed"] = _ts_to_str(accessed)

    result["delta_created_modified"] = round(modified - created, 4)
    result["delta_modified_accessed"] = round(accessed - modified, 4)

    # Heuristic anomaly checks
    if abs(result["delta_created_modified"]) < 0.01 and abs(result["delta_modified_accessed"]) < 0.01:
        result["anomaly"] = "uniform_timestamps"
    elif result["delta_created_modified"] < 0:
        result["anomaly"] = "mod_before_create"
    elif result["delta_modified_accessed"] < 0:
        result["anomaly"] = "access_before_mod"

    log_event("timestamp_check", result)
    return result


def _ts_to_str(epoch_ts: float) -> str:
    return datetime.utcfromtimestamp(epoch_ts).isoformat()