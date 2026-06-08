# Skippy — Go-Live Plan

Roadmap to take Skippy from a working dev stack to something you can run live. The server v2 backend is largely done; the gaps are client integration, hosting, and ops.

**Current state (baseline)**

| Layer | Status |
|-------|--------|
| API + ML + DB | Implemented (`/api/v2/timestamps`, async polling, SQLAlchemy cache, Alembic) |
| Firefox plugin | Removed from this repo (`d75689a`); last version predates v2 polling |
| Deployment | Dev-only: `flask run` + serveo SSH tunnel |
| CI, auth, monitoring | Missing |
| Tests | 4 ML failures (`min_duration=20` vs test expectations) + 1 store error without SQLAlchemy in host venv |

---

## Phase 1 — End-to-end works (private beta)

Goal: you and a few friends can use Skippy against a stable HTTPS API.

### 1.1 Update the Firefox plugin for v2

Plugin lives in a **separate repo**. The last in-repo version is incompatible with the current API.

- [ ] **Poll on `pending`** — first request returns `202` + `{"status": "pending"}`; retry until `ready` or `failed`
- [ ] **Parse v2 response** — use `data.intervals`, not the whole response object
- [ ] **Handle `failed`** — show/log `data.error`; optionally offer retry with `?retry=1`
- [ ] **Fix skip loop** — remove `timestamps.length - 1` off-by-one (last interval was skipped)
- [ ] **URL parsing** — support `youtu.be`, `/shorts/`, `/embed/` (server already does via `youtube_url.py`)
- [ ] **Tighter skip check** — reduce 5s interval or use `timeupdate` / `requestAnimationFrame` so short ad windows aren't missed
- [ ] **Point plugin at production URL** — stable HTTPS host, not serveo

**v2 contract reference**

| Status | HTTP | Body |
|--------|------|------|
| `pending` | 202 | `{"status": "pending"}` |
| `ready` | 200 | `{"status": "ready", "intervals": [{id, start_time, end_time, orgs}]}` |
| `failed` | 200 | `{"status": "failed", "error": "..."}` |
| Bad URL | 400 | `{"error": "..."}` |

### 1.2 Deploy the server for real (not serveo)

**Host: DigitalOcean Droplet** — see `deploy/digitalocean.md`

- [x] Pick a host — **DigitalOcean Droplet** (8 GB RAM recommended; skip App Platform)
- [x] Replace `flask run` in `entrypoint.sh` with **gunicorn** (1 worker, 4 threads)
- [x] Add reverse proxy (**Caddy**) for TLS termination (`Caddyfile`, `docker-compose.prod.yml`)
- [x] Remove hardcoded credentials from `docker-compose.yml` — use `.env`
- [x] Inject secrets via `.env` (gitignored); see `.env.example`
- [x] Add `.env.example` documenting: `DB_*`, `HUGGINGFACE_MODEL`, `CORS_ORIGINS`, `CLASSIFIER_BATCH_SIZE`, `DOMAIN`
- [x] Restrict MySQL port — `127.0.0.1:3306` locally; no public port in prod overlay
- [ ] Provision Droplet, domain DNS, firewall, and run `docker compose ... up` on the server

### 1.3 Harden job lifecycle (single-server beta)

`analysis_runner.py` uses in-process daemon threads + in-memory `_active_jobs`.

- [ ] Run **one worker process** initially (multi-worker breaks in-memory dedup)
- [ ] Add **stale `pending` recovery** — if a job has been `pending` too long with no active thread, allow re-queue (or auto-retry)
- [ ] Document restart behavior: jobs in flight are lost on deploy/restart

*Defer a proper job queue (Redis/RQ, Celery) until you need horizontal scaling.*

### 1.4 Basic abuse protection

API is fully public today.

- [ ] Per-IP rate limiting on `/api/v2/timestamps`
- [ ] Optional shared API key header from the plugin
- [ ] Timeouts on YouTube transcript fetch and model inference

### 1.5 Health checks

- [x] Add `/health` — DB connectivity check
- [x] Wire Docker `healthcheck` to `/health` (app) and `mysqladmin ping` (db)
- [x] Add DB `healthcheck` in `docker-compose.yml` so app doesn't race cold-start MySQL
- [ ] Optional: extend `/health` to verify models loaded

### 1.6 Fix tests and add CI

- [ ] Align `tests/server/ml/test_transcript_labelling.py` with `min_duration=20` in `compute_intervals` (update tests or threshold — decide intentionally)
- [ ] Add `tests/server/api/` — Flask test client for `202`/`200`/`400`, v2 response shape, CORS
- [ ] Add `.github/workflows/` — run tests in Docker (ML modules load HF models at import time)
- [ ] CI fails on regressions before merge

**Phase 1 done when:** plugin polls v2, skips ads on real videos, server runs on HTTPS with gunicorn, health check passes, CI green.

---

## Phase 2 — Public launch

Goal: strangers can install and use Skippy without you hand-holding.

### 2.1 Firefox Add-ons distribution

- [ ] AMO signing / store listing
- [ ] Privacy policy (video URLs sent to your server; what you store/cache)
- [ ] Evaluate Manifest V2 → MV3 migration
- [ ] Update README — link plugin repo, remove serveo-only instructions for production path

### 2.2 Observability

- [ ] Structured logging (request ID, video_id, analysis duration, failures)
- [ ] Error tracking (Sentry or similar) on analysis failures and 500s
- [ ] Uptime monitoring on `/health`

### 2.3 Model and image optimization

- [ ] Bake Hugging Face models into Docker image or persistent volume (avoid cold-start downloads)
- [ ] Decide CPU vs GPU for cost/latency; enable GPU compose profile if needed
- [ ] Multi-stage Docker build to trim image size where possible

### 2.4 Scaling (when single-server isn't enough)

- [ ] Replace in-process threads with a job queue
- [ ] Move `_active_jobs` dedup to DB or Redis
- [ ] Multiple replicas behind load balancer (only after queue is in place)

**Phase 2 done when:** AMO-listed extension, monitoring in place, abuse protection tested under load.

---

## Deferred / nice-to-have

Not blockers for beta or initial launch.

- [ ] Use `transcript_hash` for cache invalidation when YouTube transcript changes (model/pipeline version already triggers recompute)
- [ ] OpenAPI / formal API docs for client implementers
- [ ] Remove unused `Authlib` from `requirements.txt`
- [ ] `tests/plugin/` once plugin is back in-repo or tested in its own repo
- [ ] Global `@app.errorhandler` for JSON 500s instead of Flask HTML

---

## Suggested order of work

```
Plugin v2 integration
    → Deploy (gunicorn + TLS + real DB)
        → Single worker + stale pending recovery
            → Rate limit + /health
                → Fix tests + CI
                    → [beta] share temp add-on with prod URL
                        → [public] AMO + monitoring + model bake-in
```

---

## Quick reference — files to touch

| Task | Primary files |
|------|----------------|
| Plugin v2 | Separate plugin repo (`processor.js`, `manifest.json`, `popup.js`) |
| Production server | `server/entrypoint.sh`, `server/Dockerfile`, `server/docker-compose.yml` |
| Job lifecycle | `server/backend/analysis_runner.py`, `server/backend/interval_store.py` |
| Health | `server/app.py` |
| Rate limiting | `server/app.py` (or middleware) |
| Config docs | `server/.env.example`, `README.md` |
| Tests | `tests/server/ml/test_transcript_labelling.py`, new `tests/server/api/` |
| CI | `.github/workflows/test.yml` |
