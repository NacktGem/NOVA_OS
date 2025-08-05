#!/usr/bin/env python3
import hashlib
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parents[1] / 'frontend' / 'assets'

def hash_file(path: Path) -> str:
  sha = hashlib.sha256()
  with path.open('rb') as f:
    for chunk in iter(lambda: f.read(8192), b''):
      sha.update(chunk)
  return sha.hexdigest()

def main():
  for file in ASSETS_DIR.iterdir():
    if file.is_file():
      print(f"{file.name}: {hash_file(file)}")

if __name__ == '__main__':
  main()
