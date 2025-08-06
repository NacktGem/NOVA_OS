"""
Hash database lookup stub.

This module defines a function to check a content hash against a
database of known infringing material. In this stub, it always returns
False, indicating no violation.
"""


def check_known_hash(hash_str: str) -> bool:
    """Check if a hash exists in the known infringement database.

    Args:
        hash_str: The hexadecimal string of the content's hash.

    Returns:
        True if the hash is found (indicating infringement), False otherwise.
    """
    return False