# Lyra Agent Specification

## Responsibilities
- Guides new users through onboarding.
- Provides contextual education and receives feedback.

## API
### `/lesson`
GET query `topic` -> returns markdown text.

### `/feedback`
POST `{ user: string, message: string }` -> returns `{ status: "received" }`.

## Data
`feedback_log` table with columns `user_id`, `message`, `submitted_at`.
