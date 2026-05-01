# Agent Tools

One file per tool the agent can invoke.

## Convention

Each tool is a function that:
1. Takes structured parameters (Pydantic model)
2. Calls into `core/` to do the actual work
3. Returns a structured result

## Examples (planned)

- `generate_video.py` — request a clip generation
- `list_pending_review.py` — show clips awaiting approval
- `approve_clip.py` / `reject_clip.py` — review actions
- `schedule_post.py` — queue a post
- `get_analytics.py` — pull performance data

## What does NOT live here

Business logic. Tools delegate to `core/`. They are entry points, not implementations.
