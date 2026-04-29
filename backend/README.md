# Backend

The Lucifex backend. Python with FastAPI. Houses the business logic, agent loop, database, providers, platforms, and background workers.

## Internal organization

| Folder | Purpose |
|--------|---------|
| `api/` | HTTP endpoints. Thin transport layer. |
| `core/` | Pure domain logic. Depends on nothing else. The brain of the brain. |
| `agent/` | The AI agent loop, tools, and system prompts. |
| `db/` | SQLAlchemy models, Alembic migrations, repositories. |
| `providers/` | Adapters for AI services (LLM, video, image, TTS). |
| `platforms/` | Adapters for posting platforms (TikTok, YouTube, etc.). |
| `workers/` | Background job runner processes. |
| `jobs/` | Job type definitions — what each background task does. |
| `auth/` | Authentication, sessions, encryption primitives. |
| `observability/` | Logging, metrics, error tracking, audit log writers. |
| `config/` | Settings and environment variable loading. |
| `tests/` | Unit, integration, and end-to-end tests. |

## The dependency rule

Dependencies point inward toward `core/`. The API layer, workers, and adapters depend on `core/`. `core/` depends on nothing else. This is hexagonal architecture (also called Ports and Adapters or Clean Architecture).
