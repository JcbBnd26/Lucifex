# Workers

Long-running processes that pull jobs off the queue and execute them.

## What lives here

Worker entry points. Each worker is a script that:
1. Connects to the job queue
2. Loops forever pulling jobs of a specific type
3. Executes each job
4. Logs results

## Planned workers

- `video_worker.py` — handles video generation jobs
- `posting_worker.py` — handles posting jobs
- `analytics_worker.py` — handles analytics pull jobs

## Why split from `jobs/`

Jobs (in `jobs/`) define what work exists and how to do it. Workers run that work. Separating *what* from *how it runs* is a clean separation of concerns.

## Horizontal scalability

Multiple workers of the same type can run in parallel. The queue ensures each job is picked up by exactly one worker. Scaling = more worker processes.
