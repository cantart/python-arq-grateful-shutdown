# Repository Guidelines

## Project Structure & Module Organization
- `api.py`: FastAPI app exposing job endpoints and health checks.
- `worker.py`: ARQ worker settings, cron jobs, and lifecycle hooks.
- `jobs.py`: Async job functions (`send_email`, `process_data`, `long_running_task`).
- `docker-compose.yml`, `Dockerfile.api`, `Dockerfile.worker`: Local/dev orchestration.
- `requirements.txt`: Runtime dependencies.
- `arq-source/`: Vendored ARQ source for reference; not required to run this app.

## Build, Test, and Development Commands
- Docker (recommended):
  - Start: `docker-compose up -d` (API at `http://localhost:8005`, Redis on `6378`).
  - Logs: `docker-compose logs -f api` or `docker-compose logs -f worker`.
  - Stop: `docker-compose down` (add `-v` to remove volumes).
- Local (manual):
  - Install: `pip install -r requirements.txt`
  - Redis: `redis-server` (or `docker run -p 6378:6379 redis:7-alpine`)
  - Worker: `arq worker.WorkerSettings`
  - API: `uvicorn api:app --reload` (serves on `:8000`).

## Coding Style & Naming Conventions
- Python, PEP 8, 4‑space indentation, use type hints and docstrings.
- Naming: `snake_case` for modules/functions/vars; files like `new_feature.py`.
- Logging via `logging` (already configured in `api.py`/`worker.py`).
- Optional tools (not enforced): Black (line length 88) and Ruff. Align with existing style before introducing new tooling.

## Testing Guidelines
- Framework: Prefer `pytest`.
- Structure: `tests/` with files named `test_*.py`; unit tests for `jobs.py`, integration tests for API and worker.
- Run (once added): `pytest -q` and optionally coverage via `pytest --cov`.

## Commit & Pull Request Guidelines
- Use Conventional Commits (seen in history): `feat: ...`, `fix: ...`, `chore: ...`.
- PRs should include: clear description, linked issues, test plan/commands, and updates to docs when endpoints/compose change. Add logs or screenshots for API responses where helpful.
- Keep diffs focused; separate refactors from behavior changes.

## Security & Configuration Tips
- Configure via env vars: `REDIS_HOST`, `REDIS_PORT` (compose sets these). Avoid hard‑coding secrets.
- Health/docs: `GET /health`, Swagger UI at `/docs` (API container maps `8005:8000`).
- Validate long‑running jobs locally before enabling new cron tasks.
