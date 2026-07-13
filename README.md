# Anti-Kuddus Protocol

A student-facing accountability platform built for **BAIUST Computer Club CSE Spring Fest 2026**. Six "missions" let students report abuses, plan seating to dodge a certain professor's blind spots, negotiate bloated syllabi with AI, track a corrupt tiffin economy, send SOS flares to student captains in real time, and fact-check rules against a seeded rulebook.

> **Status of this build**: this repository was scaffolded and written by an AI pair-programmer in a sandboxed, network-isolated environment. Every file is real, complete, production-intent code — models, services, routes, React components, migrations — but **it has not been installed, booted, or exercised against a live database or live OAuth provider in that environment** (no outbound network access there). Treat this as a fully-written first cut that needs one real local run-through (`docker-compose up`, create OAuth app credentials, run migrations) before a demo, not a hand-wavy prototype. See `docs/ARCHITECTURE.md` for what's fully wired vs. what still needs your own API keys to light up.

## Design system

- **Palette**: violet/indigo primary (`#6366F1`), warm coral CTA/accent (`#FF6B57`), amber warnings (`#F59E0B`), green success (`#22C55E`), off-white paper background (`#FAF9F6`) — never pure black/white, never the default gray dashboard look.
- **Type**: Poppins (display/headers, used boldly and sparingly) + Inter (body/UI text).
- **Signature element**: the **Strike Meter** — a torn-paper "wanted poster" arc gauge that shows a strike count out of 3. It appears on the dashboard, the whistleblower mission, and the ledger, and is the one recurring visual motif that ties the "dictator vs. students" theme together.

## Quick start (local dev)

```bash
# 1. copy env files and fill in real secrets
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 2. spin up mysql + backend + frontend
docker-compose up --build

# 3. run migrations (first boot only)
docker-compose exec backend alembic upgrade head

# 4. seed demo data
docker-compose exec backend python -m app.db.seed

# frontend: http://localhost:5173
# backend docs: http://localhost:8000/docs
```

You'll need your own Google OAuth client (Google Cloud Console → Credentials → OAuth Client ID → Web application, add `http://localhost:5173` and your callback URL) and a Facebook App (Meta for Developers → Facebook Login product) — see `docs/ARCHITECTURE.md` for exact steps. Without these, email/password auth still works fully; the OAuth buttons will just fail cleanly with a "provider not configured" toast instead of silently pretending to work.

## What's deferred

These are explicitly out of scope for the hackathon timeline, not silently stubbed:
- Production S3 file storage (dev uses local `/uploads` volume; the storage layer is already abstracted behind an interface in `services/` so swapping in S3 is a config change, not a rewrite)
- Real transactional email for password reset (dev mode logs the reset link to the backend console instead)
- Rashid Sir's "impeachment tracker" view (role is modeled in the DB and route-guarded, but the dedicated screen is not built — see `docs/ARCHITECTURE.md`)
- Sentence-transformer/OpenAI embeddings for Mission 6 fall back to a TF-IDF cosine-similarity baseline unless an `OPENAI_API_KEY` is set, since the hosted embedding model isn't guaranteed to be reachable during a live demo on venue wifi

## Repo layout

See the tree in `docs/ARCHITECTURE.md` for the annotated version. Top-level: `frontend/` (React + Vite + Tailwind), `backend/` (FastAPI + SQLAlchemy 2.0 async + Alembic), `docs/`, `docker-compose.yml`.
