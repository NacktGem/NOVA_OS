# Glitch Agent Specification

## Responsibilities
- Performs device and file integrity checks.
- Detects tampering and initiates anti-forensics routines.

## API
### `/scan`
POST body: `{ "path": string }` -> returns `{ "hash": string }`.

### `/verify`
POST body: `{ "path": string, "expected_hash": string }` -> returns `{ "match": bool }`.

## Data
Stores results in `forensics_log` with fields `path`, `hash`, `timestamp`.
