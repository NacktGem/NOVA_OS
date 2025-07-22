

"""
Glitch Agent — Entropy Analyzer
Performs byte-level entropy analysis on files to detect obfuscation, compression, or potential payloads.
"""

import os
import math
from pathlib import Path
from typing import Dict, Union
from config.audit_logger import log_event
from datetime import datetime

RESULTS_DIR = Path(__file__).resolve().parents[3] / "logs" / "glitch" / "entropy_reports"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def analyze_file_entropy(file_path: Union[str, Path]) -> Dict:
    """
    Computes Shannon entropy of a file and classifies it.

    Args:
        file_path (Union[str, Path]): Path to the file to analyze.

    Returns:
        dict: {
            "file": str,
            "size_bytes": int,
            "entropy": float,
            "classification": str,
            "timestamp": str
        }
    """
    file_path = Path(file_path)
    result = {
        "file": str(file_path),
        "size_bytes": 0,
        "entropy": 0.0,
        "classification": "unknown",
        "timestamp": datetime.utcnow().isoformat()
    }

    if not file_path.exists() or not file_path.is_file():
        result["classification"] = "missing"
        return result

    with open(file_path, "rb") as f:
        data = f.read()

    if not data:
        result["classification"] = "empty"
        return result

    result["size_bytes"] = len(data)
    result["entropy"] = calculate_shannon_entropy(data)
    result["classification"] = classify_entropy(result["entropy"])
    _log_entropy(result)
    return result


def calculate_shannon_entropy(data: bytes) -> float:
    """
    Calculates Shannon entropy of the given data.

    Args:
        data (bytes): Binary data.

    Returns:
        float: Entropy value (0.0 to 8.0)
    """
    if not data:
        return 0.0

    frequency = [0] * 256
    for byte in data:
        frequency[byte] += 1

    entropy = 0.0
    data_len = len(data)
    for count in frequency:
        if count == 0:
            continue
        p_x = count / data_len
        entropy -= p_x * math.log2(p_x)

    return round(entropy, 4)


def classify_entropy(entropy: float) -> str:
    """
    Classifies entropy level into categories.

    Args:
        entropy (float): Shannon entropy score.

    Returns:
        str: Classification label.
    """
    if entropy < 3.0:
        return "low (likely plain text or code)"
    elif 3.0 <= entropy < 5.0:
        return "moderate (likely config or mixed)"
    elif 5.0 <= entropy < 7.0:
        return "high (compressed or encrypted)"
    else:
        return "very high (obfuscated or malicious payload)"


def _log_entropy(result: Dict):
    """
    Logs the result of entropy analysis.

    Args:
        result (Dict): Entropy analysis result.
    """
    file_name = Path(result["file"]).name + ".json"
    out_path = RESULTS_DIR / file_name
    with open(out_path, "w", encoding="utf-8") as f:
        import json
        json.dump(result, f, indent=2)

    log_event("entropy_scan", result)