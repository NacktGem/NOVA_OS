# Riven Agent Specification

## Responsibilities
- Monitors sessions for anomalies.
- Scores risk and triggers lockdowns.

## API
### `/session`
POST `{ user: string, ip: string }` -> returns `{ risk: number }`.

### `/lock`
POST `{ user: string }` (Nova-only) -> returns `{ locked: bool }`.

## Data
`session_watch` table: `user`, `ip`, `risk_score`, `timestamp`.
