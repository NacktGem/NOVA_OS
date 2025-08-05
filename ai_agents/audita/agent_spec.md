# Audita Agent Specification

## Responsibilities
- Handles legal compliance, external requests, and audit logging.
- Manages response to law enforcement and user data requests.

## API
### `/request`
POST `{ type: string, reference: string }` -> returns `{ ticket: string }`.

### `/log`
POST `{ event: string, actor: string }` -> returns `{ recorded: bool }`.

## Data
`audit_log` table: `id`, `event`, `actor`, `timestamp`, `signature`.
