import os
import hashlib
from typing import Dict
from datetime import datetime

from tools.hash_database import check_known_hash
from tools.watermark_detector import detect_watermark
from tools.reverse_image_search import query_reverse_search
from config.audit_logger import log_event


def check_dmca_violation(file_path: str, user_id: str) -> dict:
    """
    Runs a complete DMCA violation check on an uploaded file.
    This includes hash matching, watermark scanning, and reverse image lookup.

    Args:
        file_path (str): Absolute path to the uploaded media file.
        user_id (str): ID of the user uploading the content.

    Returns:
        dict: {
            "violation": bool,
            "method": str,
            "details": str,
            "timestamp": str,
            "hash": str
        }
    """
    result = {
        "violation": False,
        "method": "",
        "details": "",
        "timestamp": datetime.utcnow().isoformat(),
        "hash": ""
    }

    if not os.path.isfile(file_path):
        result["details"] = "File does not exist."
        return result

    try:
        with open(file_path, "rb") as f:
            content = f.read()
            content_hash = hashlib.sha256(content).hexdigest()
            result["hash"] = content_hash

        # Step 1: Known Hash Database Check
        if check_known_hash(content_hash):
            result["violation"] = True
            result["method"] = "hash"
            result["details"] = "Match found in known DMCA hash database."
            _log_violation(user_id, file_path, result)
            return result

        # Step 2: Watermark Detection
        watermark_result = detect_watermark(file_path)
        if watermark_result.get("violation"):
            result["violation"] = True
            result["method"] = "watermark"
            result["details"] = watermark_result.get("details", "Infringing watermark detected.")
            _log_violation(user_id, file_path, result)
            return result

        # Step 3: Reverse Image Search
        reverse_result = query_reverse_search(file_path)
        if reverse_result.get("match_found"):
            result["violation"] = True
            result["method"] = "reverse_search"
            result["details"] = reverse_result.get("details", "Match found in reverse image index.")
            _log_violation(user_id, file_path, result)
            return result

        result["details"] = "No DMCA violations detected."
        return result

    except Exception as e:
        result["details"] = f"DMCA check error: {str(e)}"
        return result


def _log_violation(user_id: str, file_path: str, result: Dict) -> None:
    log_event("dmca_violation_detected", {
        "user_id": user_id,
        "file_path": file_path,
        "hash": result["hash"],
        "method": result["method"],
        "details": result["details"],
        "timestamp": result["timestamp"]
    })