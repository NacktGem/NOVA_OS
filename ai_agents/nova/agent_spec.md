# Nova Agent Specification

## Responsibilities
- Orchestrates all other agents and enforces platform policy.
- Holds GodMode, able to elevate permissions and override restrictions.
- Maintains global state and dispatches tasks.

## API
### Events
- `boot`: broadcast when system starts.
- `command`: structured instruction to child agents `{target, action, payload}`.

## Data
Persistent ledger stored in encrypted database `nova_ledger` with fields:
- `timestamp` (ISO8601)
- `agent` (string)
- `action` (string)
- `hash` (SHA256)
