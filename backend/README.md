# Backend

The Lucifex backend. Python 3.12 with FastAPI. Houses the business logic, agent loop, database, providers, platforms, and background workers.

## Internal organization

| Folder | Purpose |
|--------|---------|
| `src/lucifex/api/` | HTTP endpoints. Thin transport layer. |
| `src/lucifex/core/` | Pure domain logic. Depends on nothing else. The brain of the brain. |
| `src/lucifex/agent/` | The AI agent loop, tools, and system prompts. |
| `src/lucifex/db/` | SQLAlchemy models, Alembic migrations, repositories. |
| `src/lucifex/providers/` | Adapters for AI services (LLM, video, image, TTS). |
| `src/lucifex/platforms/` | Adapters for posting platforms (TikTok, YouTube, etc.). |
| `src/lucifex/workers/` | Background job runner processes. |
| `src/lucifex/jobs/` | Job type definitions — what each background task does. |
| `src/lucifex/auth/` | Authentication, sessions, encryption primitives. |
| `src/lucifex/observability/` | Logging, metrics, error tracking, audit log writers. |
| `src/lucifex/config/` | Settings and environment variable loading. |
| `tests/` | Unit, integration, and end-to-end tests. |

## Layout

The backend uses the `src/` layout, with the importable package at `backend/src/lucifex/`. Imports across the codebase look like:

```python
from lucifex.core.clips import approve_clip
from lucifex.providers.llm.anthropic import AnthropicProvider
```

The src layout forces an editable install before imports resolve, which catches packaging bugs early and ensures tests run against the installed package the way users would.

## The dependency rule

Dependencies point inward toward `core/`. The API layer, workers, and adapters depend on `core/`. `core/` depends on nothing else. This is hexagonal architecture (also called Ports and Adapters or Clean Architecture).

## Local development

From the `backend/` directory:

```bash
# Create and activate a virtual environment (Python 3.12)
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate         # macOS/Linux

# Install the package in editable mode with dev dependencies
pip install -e ".[dev]"
```

Common commands once installed:

| Command | Purpose |
|---------|---------|
| `ruff check .` | Lint the codebase. |
| `ruff format .` | Auto-format the codebase. |
| `mypy src` | Type-check the package. |
| `pytest` | Run all tests. |
| `pytest tests/unit` | Run unit tests only. |

## See also

- `pyproject.toml` — package metadata, dependencies, tool configuration
- `../docs/architecture.md` — full system design
- `../docs/decision_log.md` — architectural decisions
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
