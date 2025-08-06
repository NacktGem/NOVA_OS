"""
Watermark detection stub.

This module contains a placeholder function to detect watermarks in media
files. Real implementations could use image processing or machine learning
techniques to identify infringing watermarks.
"""

from typing import Dict


def detect_watermark(file_path: str) -> Dict:
    """Detect watermarks in a file.

    Args:
        file_path: Path to the file to check.

    Returns:
        A dict with keys 'violation' (bool) and 'details' (str) describing
        the result. Always returns no violation in this stub.
    """
    return {"violation": False, "details": ""}