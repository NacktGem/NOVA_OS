#!/usr/bin/env python3
"""
Utility to compute SHA‑256 hashes for frontend asset files.

Run this script to list the filename and SHA‑256 digest of each file in the
frontend/assets directory. This can be used to verify asset integrity.
"""

import hashlib
from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parents[1] / 'frontend' / 'assets'


def hash_file(path: Path) -> str:
    """Return the SHA‑256 hash of a file."""
    sha = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha.update(chunk)
    return sha.hexdigest()


def main() -> None:
    for file in ASSETS_DIR.iterdir():
        if file.is_file():
            print(f"{file.name}: {hash_file(file)}")


if __name__ == '__main__':
    main()