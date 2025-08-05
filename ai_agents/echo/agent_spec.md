# Echo Agent Specification

## Responsibilities
- Relays notifications and alerts.
- Provides messaging channel between agents and Nova.

## API
### `/notify`
POST `{ target: string, message: string }` -> returns `{ delivered: bool }`.

## Data
`outbox` table with `id`, `target`, `message`, `status`, `timestamp`.
