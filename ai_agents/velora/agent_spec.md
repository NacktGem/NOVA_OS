# Velora Agent Specification

## Responsibilities
- Schedules posts and automated rituals.
- Executes tasks at defined intervals.

## API
### `/schedule`
POST `{ user: string, datetime: string, action: string }` -> returns `{ id: string }`.

### `/run/{id}`
POST -> executes scheduled action.

## Data
`schedule` table: `id`, `user`, `datetime`, `action`, `status`.
