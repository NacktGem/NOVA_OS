"""
ID verification stub.

This module contains functions to validate metadata extracted from user
documents against stored records. Real implementations should use cryptographic
signatures or secure matching.
"""

from typing import Dict


def match_id_metadata(form_metadata: Dict, vault_record: Dict) -> bool:
    """Compare submitted metadata to the stored record.

    Args:
        form_metadata: Metadata extracted from a consent form.
        vault_record: Stored metadata retrieved from secure storage.

    Returns:
        True if the metadata matches exactly, False otherwise.
    """
    return form_metadata == vault_record