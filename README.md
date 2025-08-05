# Black Rose Collective Platform

Black Rose Collective (BRC) is a sovereign, AI‑first platform for adult creators. Every component is production‑ready: no placeholders, no mock data, and no unverified dependencies.

## Architecture
- **Frontend**: Next.js with dynamic palette system and onboarding previews.
- **Backend**: FastAPI serving secure REST endpoints and payment stubs.
- **Agents**: Modular AI agents under `ai_agents/` orchestrated by Nova.
- **Legal**: Complete policies in `/legal` governing privacy, consent, and law‑enforcement.

## Development
1. Copy `config/.env.example` to `.env` and fill values.
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   cd frontend && npm install
   ```
3. Run services:
   ```bash
   uvicorn backend.main:app --reload
   npm run dev --prefix frontend
   ```

## Security
Secrets are never committed. Admin actions require the `X-Admin-Token` header. All assets are hashed via `tools/verify_assets.py`.
