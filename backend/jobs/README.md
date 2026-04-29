# Job Definitions

What kinds of background work exist and how each is performed.

## Convention

One file per job type:

- `generate_video.py` — generate a clip from a prompt
- `render_clip.py` — produce a platform-ready render from a clip (passthrough in MVP)
- `post_to_platform.py` — publish a render to a platform
- `pull_analytics.py` — refresh performance data from a platform
- `refresh_oauth.py` — refresh expiring OAuth tokens

## Each job

- Takes a `payload` (parameters from the database row)
- Calls into `core/`, `providers/`, or `platforms/` to do real work
- Returns a result that gets stored in `job_runs`

## Idempotency

Every job execution must be idempotent. If a job is retried, it should produce the same result as running it once. Idempotency keys on the `jobs` table prevent duplicate job creation; idempotent execution prevents duplicate side effects.

## See also

- `docs/decision_log.md` — DEC-012 (idempotency keys on all jobs)
