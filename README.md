# ARQ + FastAPI — Graceful Shutdown Notes

This repo is a minimal ARQ (Async Redis Queue) + FastAPI setup used to observe and document worker shutdown behavior in containers.

## Key Takeaways

- Graceful period: After a container receives `SIGTERM`, each ARQ worker respects `job_completion_wait` and continues trying to finish in‑flight jobs until that period ends.
- Forced kill risk: If `SIGKILL` arrives before the grace period ends, shutdown is not graceful: running jobs are not cancelled and will not be retried immediately on restart.
- Practical impact: Restarts that escalate to `SIGKILL` can leave jobs in an unfinished state longer than expected; plan your deployment grace period accordingly.

## Recommendations

- Tune timeouts: Ensure the platform’s termination grace (e.g., Kubernetes `terminationGracePeriodSeconds`) > `job_completion_wait` + expected job cancellation/cleanup time.
- Prefer clean exits: Avoid `SIGKILL` during normal rollouts; let workers drain with `SIGTERM`.
- If SIGKILL is unavoidable: Consider shorter jobs or idempotent tasks without setting `job_completion_wait`, so interrupted jobs can be retried sooner on restart.

## Reproduce Locally

- Start stack: `docker-compose up -d` (API on `http://localhost:8005`).
- Enqueue a long job via `POST /jobs/enqueue` with `function_name="long_running_task"` and a long `duration`.
- Stop the worker service: `docker stop -t 5 <worker_container_id>` (5s grace).
- The worker will not log job cancellation if `SIGKILL` arrives before `job_completion_wait` ends, so that job will not be retried immediately on restart.

## Relevant Files

- `worker.py`: ARQ worker settings (`job_completion_wait`, timeouts, functions).
- `api.py`: FastAPI endpoints for enqueuing and inspecting jobs.
- `jobs.py`: Example job functions, including a long‑running task.

For full project usage, see inline docs in the files and the `docker-compose.yml` service definitions.
