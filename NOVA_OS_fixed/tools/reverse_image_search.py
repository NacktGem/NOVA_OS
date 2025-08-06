"""
Reverse image search stub.

This module defines a placeholder function that simulates a reverse image
search. In production, integrate with a third-party API or implement your
own image indexing.
"""

from typing import Dict


def query_reverse_search(file_path: str) -> Dict:
    """Perform a reverse image search.

    Args:
        file_path: Path to the file to search.

    Returns:
        A dict with keys 'match_found' (bool) and 'details' (str) describing
        the result. Always returns no match in this stub.
    """
    return {"match_found": False, "details": ""}