# Chunk B — Lucifex Folder Scaffold

You are working in the Lucifex project repository. Chunk A established the foundation: `.gitignore`, root `README.md`, `docs/`, and `chunks/`. Your job in Chunk B is to scaffold the full folder structure of the project — every folder from the architecture document, with a README anchor inside each one.

You will not write any code. You will not create any `pyproject.toml`, `package.json`, `Dockerfile`, or other configuration files. Those come in later chunks. You will not create any `__init__.py` files yet — Python package initialization happens in Chunk C alongside environment setup.

Every folder you create gets exactly one file inside it: a `README.md` describing the purpose of the folder. This serves two functions: git tracks the folder (git ignores empty folders), and future-you (or any collaborator) can open any folder and immediately understand what belongs there.

When you are finished, report back with confirmation of each operation and show the final file tree.

---

## Operation 1 — Create `backend/` and its subfolders

Create the following folder structure under the project root:

```
backend/
├── api/
├── core/
├── agent/
│   ├── tools/
│   └── prompts/
├── db/
│   ├── models/
│   ├── migrations/
│   └── repositories/
├── providers/
│   ├── llm/
│   ├── video_generation/
│   ├── image_generation/
│   └── tts/
├── platforms/
├── workers/
├── jobs/
├── auth/
├── observability/
├── config/
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

Inside each folder, create a `README.md` file with the content specified below.

---

### `backend/README.md`

```
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
```

---

### `backend/api/README.md`

```
# API Layer

HTTP endpoints exposed to the outside world. The frontend calls these. External integrations may eventually call these.

## What lives here

- Route definitions (organized by domain — `routes/clips.py`, `routes/campaigns.py`, etc.)
- Request validation (Pydantic schemas)
- Response formatting
- HTTP-specific concerns (status codes, headers, CORS)

## What does NOT live here

- Business logic. This layer is *transport*, not logic. An endpoint should parse the request, call a function in `core/`, and format the response. Twenty lines per endpoint. If the endpoint is doing math, calling external services, or making decisions, that work belongs in `core/`.
```

---

### `backend/core/README.md`

```
# Core Domain Logic

The most important folder in the entire backend. The brain of the brain.

## What lives here

The rules of the system. Pure functions and services that take inputs, apply rules, and return outputs. Examples: "what does it mean to approve a clip?", "how do we compute campaign aggregates?", "what's the workflow when a post fails three times?"

## The defining property

Code in `core/` does NOT know about HTTP. Does NOT know about databases. Does NOT know about external APIs. It operates on data structures (Pydantic models, dataclasses) and returns data structures. It is testable without spinning up a server, a database, or a network.

## Why this matters

Business logic tangled with infrastructure is fragile. Keep `core/` pure and the rest of the system can change underneath it. The API can be swapped for a CLI. Postgres can be replaced. The agent's LLM provider can change. Core stays stable.

## Organization

Subfolders by domain: `core/clips/`, `core/campaigns/`, `core/agent/`, `core/posting/`, etc. Each subdomain owns its services, validators, and types.
```

---

### `backend/agent/README.md`

```
# Agent

The AI agent that operates Lucifex on behalf of the operator. Conceptually part of `core/`, but separated because it is large and novel enough to deserve its own region.

## Structure

- `loop.py` — the main agent loop (LLM call → process tool calls → repeat)
- `tools/` — each tool the agent can call, one file per tool
- `prompts/` — system prompts as text/markdown files, versioned

## Tools as functions

Each tool is a simple function that takes structured parameters and returns structured results. Behind the scenes, the function calls into `core/` to do real work. The agent does NOT have its own business logic — it is a *driver* that calls the same core primitives a human would call through the API.

## Prompts as files

Prompts live in `prompts/` as markdown files, not hardcoded strings. They are diffable in git, reviewable, A/B-testable, and versioned by snapshot (referenced by `agent_conversations.system_prompt_used` so old conversations remain debuggable when prompts evolve).
```

---

### `backend/agent/tools/README.md`

```
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
```

---

### `backend/agent/prompts/README.md`

```
# Agent System Prompts

Markdown files containing the system prompts the agent uses.

## Why files, not strings

- Diffable in git
- Reviewable in pull requests
- Versionable by snapshot (referenced in `agent_conversations.system_prompt_used`)
- A/B-testable
- Editable by non-coders

## Convention

- `base.md` — the foundational system prompt every conversation inherits
- `channel_voice_template.md` — the structure for per-channel voice prompts (filled in by channel data at runtime)
- Other named prompts as features grow

Prompts evolve frequently. Versioning by snapshot (storing the active prompt text on the conversation row at conversation start) ensures historical conversations remain reproducible.
```

---

### `backend/db/README.md`

```
# Database Layer

SQLAlchemy models, Alembic migrations, and database session management.

## Structure

- `models/` — SQLAlchemy table definitions, one file per major table or domain
- `migrations/` — Alembic-generated change files, versioned in git
- `repositories/` — query helpers grouped by table (optional — added when query duplication appears)
- `session.py` — database connection setup and session factory
- `seed.py` — initial or test data seeding (added when needed)

## Migrations discipline

Every schema change is a migration. Migrations are versioned in git, applied in order, and reversible. Manual database edits are forbidden — they break reproducibility across environments.

## See also

- `docs/architecture.md` — full data model documentation (20 tables)
- `docs/decision_log.md` — DEC-008 (Postgres + SQLAlchemy + Alembic)
```

---

### `backend/db/models/README.md`

```
# SQLAlchemy Models

Table definitions as Python classes.

## Convention

One file per table, or grouped by closely-related domain when natural (e.g., `agent.py` could hold `AgentConversation`, `AgentMessage`, `AgentToolCall` together).

## Shared base

A `base.py` file holds the SQLAlchemy declarative base and any mixins for shared fields (timestamps, soft delete, etc.). Every model inherits from this.

## Common fields (by convention)

- `id` — UUID primary key
- `created_at` — timestamp, set on insert
- `updated_at` — timestamp, auto-updates on change
- `deleted_at` — nullable timestamp, for soft delete (only on tables where deletion is meaningful)

Append-only tables (`analytics_snapshots`, `audit_log`, `status_history`, `agent_messages`, `job_runs`) get only `created_at`.
```

---

### `backend/db/migrations/README.md`

```
# Alembic Migrations

Versioned schema changes. Generated by Alembic, committed to git, applied in order.

## Workflow

1. Modify a SQLAlchemy model in `models/`
2. Run `alembic revision --autogenerate -m "<description>"`
3. Review the generated migration file in `versions/`
4. Run `alembic upgrade head` to apply

## Discipline

- Never edit applied migrations. Create a new one.
- Always review autogenerated migrations before applying — Alembic is good but not perfect.
- Migrations should be reversible (Alembic generates `downgrade` automatically; verify it).
```

---

### `backend/db/repositories/README.md`

```
# Repositories

Query helpers grouped by table or domain.

## Purpose

Common queries deserve a single home. "Get all clips pending review for channel X." "Find posts from the last 7 days with their analytics." Without repositories, the same query gets written five different ways in five different services.

## When to add a repository

When a query is needed in more than one place, or when a query is non-trivial enough to deserve a name. Don't preemptively wrap every simple `get_by_id` — that's bloat.

## Convention

`repositories/clips.py` for clip queries. `repositories/posts.py` for post queries. Each function takes a session and parameters; returns models or DTOs.
```

---

### `backend/providers/README.md`

```
# Providers

Adapters for external AI services. Where BYOLLM lives.

## The pattern

Each external service (LLM, video generation, image generation, TTS) sits behind a common interface defined in `base.py`. Each concrete provider implements that interface. Code outside `providers/` only ever talks to the abstract interface, never to a concrete provider.

## Structure

- `base.py` — abstract interfaces (`LLMProvider`, `VideoGenerationProvider`, etc.)
- `llm/` — LLM adapters (Anthropic, OpenAI, Google)
- `video_generation/` — video generation adapters (Kling, Runway, Veo, Sora)
- `image_generation/` — image generation adapters
- `tts/` — text-to-speech adapters
- `registry.py` — maps provider names from the database to concrete implementations

## Why this matters

AI tools change rapidly. Hardcoding "we use Kling" means rewriting when Veo surpasses it. The adapter pattern means swapping providers is a configuration change.

## See also

- `docs/decision_log.md` — DEC-003 (Provider-agnostic adapter pattern, BYOLLM)
```

---

### `backend/providers/llm/README.md`

```
# LLM Providers

Adapters for large language model services. Each implements the `LLMProvider` interface from `../base.py`.

## Planned providers

- `anthropic.py` — Claude (default for Phase 2)
- `openai.py` — GPT models
- `google.py` — Gemini models

## Interface (concept)

```python
class LLMProvider:
    async def complete(messages, model, params) -> Completion
    async def complete_with_tools(messages, model, tools, params) -> ToolCallResult
```

Each adapter handles its provider's specific API quirks, authentication, error handling, and response normalization.
```

---

### `backend/providers/video_generation/README.md`

```
# Video Generation Providers

Adapters for AI video generation services. Each implements the `VideoGenerationProvider` interface from `../base.py`.

## Planned providers

- `kling.py` — Kling AI (default for Phase 1)
- `runway.py` — Runway
- `veo.py` — Google Veo
- `sora.py` — OpenAI Sora
- `grok.py` — xAI video generation

## Interface (concept)

```python
class VideoGenerationProvider:
    async def generate(prompt, params) -> GenerationJob
    async def get_status(job_id) -> JobStatus
    async def get_result(job_id) -> VideoResult
```

Generation is asynchronous on every provider — the adapter abstracts the polling, webhook, or callback pattern into a uniform job-based interface.
```

---

### `backend/providers/image_generation/README.md`

```
# Image Generation Providers

Adapters for AI image generation services. Used for thumbnails, channel art, and any still-image needs.

## Status

Not used in Phase 0-3 MVP. Folder exists as a placeholder for the architecture.

## Interface (concept)

```python
class ImageGenerationProvider:
    async def generate(prompt, params) -> ImageResult
```
```

---

### `backend/providers/tts/README.md`

```
# Text-to-Speech Providers

Adapters for AI voice synthesis services.

## Status

Not used in Phase 0-3 MVP. Folder exists as a placeholder for the architecture, since voiceovers will likely be needed for long-form YouTube content in later phases.

## Interface (concept)

```python
class TTSProvider:
    async def synthesize(text, voice, params) -> AudioResult
```
```

---

### `backend/platforms/README.md`

```
# Platforms

Adapters for content distribution platforms. Same pattern as `providers/`, different domain.

## The pattern

Each platform (TikTok, YouTube, Instagram, Facebook) implements a common `PostingPlatform` interface. The interface to the rest of the system is uniform: `platform.post(render, caption, schedule_time) -> PostResult`. Internally, each adapter handles its own API quirks, OAuth flow, rate limits, and error handling.

## Structure

- `base.py` — the `PostingPlatform` interface
- `youtube.py` — YouTube adapter (Phase 3 anchor — see DEC-009)
- `tiktok.py` — TikTok adapter (Phase 4)
- `instagram.py` — Instagram adapter (Phase 4)
- `facebook.py` — Facebook adapter (Phase 4)
- `registry.py` — maps platform names from the database to concrete implementations

## OAuth

Each adapter owns its OAuth dance independently. Tokens are stored encrypted in the `platforms` database table.

## See also

- `docs/decision_log.md` — DEC-009 (YouTube as Phase 3 anchor)
```

---

### `backend/workers/README.md`

```
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
```

---

### `backend/jobs/README.md`

```
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
```

---

### `backend/auth/README.md`

```
# Auth

Authentication and security primitives.

## What lives here

- Password hashing (bcrypt or argon2)
- JWT or session token handling
- OAuth flow helpers (delegated to platform/provider adapters where appropriate)
- Encryption/decryption for secrets stored in the database
- Role and permission checking
- Rate limiting helpers

## Discipline

This folder is small but critical. Mistakes here are security holes.

Every function in this folder is a thin wrapper around well-tested libraries (`bcrypt`, `cryptography`, `python-jose`). We do NOT roll our own crypto. Reading library documentation carefully is the skill here, not cleverness.

## Encryption strategy

The encryption key lives in environment variables (or a secrets manager in production). Tokens and API keys are encrypted before insert and decrypted on read. Database leak does NOT mean credential leak.
```

---

### `backend/observability/README.md`

```
# Observability

The system observing itself. Logging, errors, metrics, audit log writers, health checks.

## What lives here

- `logging.py` — structured logging configuration (structlog)
- `errors.py` — Sentry integration
- `metrics.py` — performance and business metrics
- `audit.py` — helper functions for writing `audit_log` entries
- `health.py` — health check logic for the API

## Logging philosophy

Logs are data, not text. Every log line is JSON with fields like `level`, `event`, `clip_id`, `error`, `duration_ms`. Structured logs are searchable, filterable, aggregatable. Plain-text logs are not.

## Why a folder, not just imports

Centralizing the configuration (log format, error reporter setup, metrics collectors) means a single source of truth. Every other module in the backend imports `from observability import logger` and gets a properly configured logger.
```

---

### `backend/config/README.md`

```
# Config

Settings, environment variables, and feature flags.

## What lives here

- `settings.py` — typed settings class (using `pydantic-settings`) that loads from environment variables
- `feature_flags.py` — runtime toggles for experimental features (added when needed)

## Typed settings

Don't read `os.environ.get("DATABASE_URL")` from random places in the codebase. Define a `Settings` class with typed fields. Validation happens at startup, not when something tries to use a missing setting at 3am. Every setting the app expects is documented in one place.

## Local development

Local development uses `.env` files (gitignored). Production uses real environment variables injected by the deployment platform. The `Settings` class works the same in both cases.
```

---

### `backend/tests/README.md`

```
# Tests

The safety net.

## Structure

Mirrors the backend structure:

- `unit/` — fast, isolated tests of individual functions. Most tests should be these.
- `integration/` — tests of pieces working together with a real database.
- `e2e/` — end-to-end tests of full flows through the API. Slowest, fewest.

## The testing pyramid

Many unit tests, fewer integration tests, very few E2E tests. Inverting this leads to slow, flaky, hard-to-debug test suites.

## What gets tested

Phase 0 ships with one E2E test (login works). Subsequent phases add tests for the new code they introduce. The discipline is: every non-trivial function in `core/` gets unit tests. Adapters get integration tests with mocked external APIs. Critical user flows get E2E tests.
```

---

### `backend/tests/unit/README.md`

```
# Unit Tests

Fast, isolated tests of individual functions and classes.

## Conventions

- No I/O. No database. No network. No filesystem (mock if needed).
- One test file per source file, mirroring the source structure (`tests/unit/core/clips/test_approval.py` tests `core/clips/approval.py`).
- Test names describe what is being verified (`test_clip_cannot_be_approved_when_already_rejected`).
```

---

### `backend/tests/integration/README.md`

```
# Integration Tests

Tests of multiple components working together with real infrastructure (database, file storage).

## Conventions

- Real database, but isolated per test (transactions rolled back, or per-test schema).
- Real file storage if needed (use a test bucket or local equivalent).
- External APIs are still mocked — we don't hit Kling or YouTube in tests.
- Slower than unit tests; fewer in number.
```

---

### `backend/tests/e2e/README.md`

```
# End-to-End Tests

Full user flows tested through the public API.

## Conventions

- Spin up the full app (API server + database + workers).
- Drive the test through the API, the way a real client would.
- Used sparingly — these are slow.
- Phase 0 has one: login works.
```

---

## Operation 2 — Create `frontend/` and its subfolders

Create the following folder structure:

```
frontend/
├── app/
├── components/
├── features/
├── lib/
├── styles/
├── public/
└── tests/
```

Inside each folder, create a `README.md` with the content specified below.

---

### `frontend/README.md`

```
# Frontend

The Lucifex frontend. Next.js with React. The dashboard and agent chat interface.

## Internal organization

| Folder | Purpose |
|--------|---------|
| `app/` | Next.js routes (file-based routing). |
| `components/` | Reusable generic UI primitives (buttons, inputs, modals). |
| `features/` | Feature-specific code grouped by domain. |
| `lib/` | API client, utilities, custom hooks. |
| `styles/` | Tailwind config and design tokens. |
| `public/` | Static assets. |
| `tests/` | Frontend tests. |

## Architectural principle

Pages depend on features. Features depend on components and `lib`. Components and `lib` depend on nothing else in the project. Dependencies flow one direction.
```

---

### `frontend/app/README.md`

```
# App (Routes)

Next.js file-based routing. Files in this folder map to URL paths.

## Convention

- `app/dashboard/page.tsx` → `/dashboard`
- `app/agent/page.tsx` → `/agent`
- `app/login/page.tsx` → `/login`

## What pages should be

Thin. Pages assemble feature components and pass them data. Heavy logic does NOT live in pages — it lives in features or `lib`.

## Planned MVP routes

- `/login` — authentication
- `/agent` — chat interface (primary view)
- `/review` — clip review queue
- `/settings` — provider and platform configuration
```

---

### `frontend/components/README.md`

```
# Components

Reusable generic UI primitives.

## What lives here

Generic components used across features. Buttons, inputs, modals, cards, tables, tooltips. Things with no business meaning, only visual purpose.

## What does NOT live here

Specific components like `ClipReviewCard` or `CampaignDashboard`. Those go in `features/`.

## Generic vs specific

`components/Button.tsx` — generic. Lives here.
`features/clips/ClipReviewCard.tsx` — specific. Lives in features.

Mixing these is how component folders become 200-file dumping grounds.
```

---

### `frontend/features/README.md`

```
# Features

Domain-organized UI. Each major area of the app gets a folder.

## Planned features (MVP)

- `agent-chat/` — the chat interface
- `clip-review/` — review queue and approval UI
- `channels/` — channel management
- `settings/` — provider and platform configuration

## Colocation principle

Code that changes together lives together. Each feature folder contains its components, hooks, API calls, and types. Working on clip review touches one folder. Spreading these across `components/`, `hooks/`, `api/`, and `types/` means jumping between folders for every change.

This pattern is called feature-based organization and is the modern preferred approach for medium-to-large frontends.
```

---

### `frontend/lib/README.md`

```
# Lib

Utilities and infrastructure used across features.

## What lives here

- `api.ts` — wraps fetch calls to the Lucifex backend
- `auth.ts` — authentication helpers
- `format.ts` — formatting utilities (dates, numbers, currency)
- Custom React hooks that aren't tied to a single feature
- TypeScript type definitions shared across features

## What does NOT live here

Feature-specific code. If a hook is only used in clip review, it lives in `features/clip-review/`, not here.
```

---

### `frontend/styles/README.md`

```
# Styles

Design system configuration.

## What lives here

- `globals.css` — global styles
- Tailwind configuration
- Design tokens (colors, spacing, typography) when they outgrow the Tailwind config

## Discipline

Most styling lives inline as Tailwind classes on components. This folder holds only the things that don't fit there: global styles, tokens, and Tailwind setup.
```

---

### `frontend/public/README.md`

```
# Public

Static assets served directly by Next.js.

## What lives here

- Images (logos, favicons, illustrations)
- Fonts (if self-hosted)
- robots.txt, sitemap.xml when added

## Convention

Files in `public/` are served from the root. `public/logo.svg` is accessed at `/logo.svg`.
```

---

### `frontend/tests/README.md`

```
# Frontend Tests

Component and integration tests for the frontend.

## Tools

- Vitest or Jest for unit/component tests
- Playwright for end-to-end tests (added when needed)

## Convention

Tests live alongside or inside this folder, mirroring the source structure.
```

---

## Operation 3 — Create `infra/` and its subfolders

Create the following folder structure:

```
infra/
├── docker/
├── deployment/
├── github-actions/
└── scripts/
```

Inside each folder, create a `README.md` with the content specified below.

---

### `infra/README.md`

```
# Infra

Infrastructure and deployment configuration. The foundation that runs the application.

## Internal organization

| Folder | Purpose |
|--------|---------|
| `docker/` | Dockerfiles for backend, frontend, and worker processes. |
| `deployment/` | Configuration for the hosting platform (Railway, Fly.io, Render). |
| `github-actions/` | CI/CD workflows. |
| `scripts/` | One-off operational scripts. |

## Why infra is separate

Deployment is not application logic. The instructions for "how to run this on a server" are different from the application itself. Mixing them creates lock-in to specific environments and confuses contributors about what is the app vs what is the plumbing.
```

---

### `infra/docker/README.md`

```
# Docker

Dockerfiles describe how to build container images for the backend, frontend, and worker processes.

## Planned files

- `backend.Dockerfile` — builds the FastAPI server image
- `worker.Dockerfile` — builds the worker image (often the same as backend with a different entrypoint)
- `frontend.Dockerfile` — builds the Next.js production image

## Why containers

A container image is built once and runs identically in development, staging, and production. No "works on my machine" problems. The Dockerfile is the recipe; the image is the meal.
```

---

### `infra/deployment/README.md`

```
# Deployment

Configuration for the hosting platform.

## Status

Specific platform choice deferred to Phase 0 (currently leaning Railway or Fly.io for backend, Vercel for frontend). The configuration files for the chosen platform live here.

## What goes here

- Platform-specific configs (e.g., `railway.toml`, `fly.toml`)
- Environment variable documentation (the `.env.example` files belong here too)
- Resource declarations (databases, storage buckets, cron schedules)
```

---

### `infra/github-actions/README.md`

```
# GitHub Actions

CI/CD workflows.

## Note on location

GitHub Actions requires workflows to live in `.github/workflows/` at the repository root, not in this folder. The actual workflow files will live there.

This folder holds:
- Documentation about the CI/CD strategy
- Reusable composite actions (when needed)
- Scripts called from workflows
```

---

### `infra/scripts/README.md`

```
# Scripts

One-off operational scripts. Things you run occasionally that aren't part of the main app flow.

## Examples (planned)

- `backup_db.sh` — back up the production database
- `seed_dev.py` — populate a development database with test data
- `migrate_storage.py` — move storage from one provider to another (if ever needed)
- `rotate_keys.py` — rotate encryption keys

## Convention

Each script should be runnable standalone with a clear purpose at the top. Destructive scripts should require confirmation flags (`--yes-really`).
```

---

## Operation 4 — Create the `output/` folder

Create a folder named `output/` at the project root. Inside, create a `README.md` with this content:

```
# Output

Operational outputs from the running application. Generated files, exported reports, temporary artifacts.

## Why this folder is gitignored

The `.gitignore` excludes everything in `output/` EXCEPT this README. The folder is for runtime artifacts, not source. Tracking generated content in git pollutes history and bloats the repo.

The README is tracked so the folder exists in the repo (git doesn't track empty folders) and so contributors understand what the folder is for.
```

This README is intentionally tracked — see `.gitignore` Section 5 for the `!output/README.md` exception.

---

## Operation 5 — Save this chunk document

Save this entire chunk document into the `chunks/` folder as `chunk_b_folder_scaffold.md`.

---

## Constraints

Do not create any files other than `README.md` files inside the folders specified above, plus this chunk document in `chunks/`.

Specifically, do NOT create:
- Any Python files (`.py`)
- Any TypeScript or JavaScript files (`.ts`, `.tsx`, `.js`, `.jsx`)
- `pyproject.toml`, `setup.py`, `requirements.txt`
- `package.json`, `tsconfig.json`, `next.config.js`
- Any `Dockerfile`
- Any `__init__.py` files (Python packaging happens in Chunk C)
- The `.github/` folder (CI/CD setup is its own chunk later)

Do not run any git commands. Do not run any package manager commands. Do not run any terminal commands except those required to create folders on Windows.

---

## When you are finished

Report back with:

1. Confirmation of the `backend/` tree (with all subfolders and README files).
2. Confirmation of the `frontend/` tree.
3. Confirmation of the `infra/` tree.
4. Confirmation of the `output/` folder with its README.
5. Confirmation that `chunks/chunk_b_folder_scaffold.md` exists.
6. The complete file tree of the project root (folders + files).

Do not stage, commit, or push anything. The operator will run git commands manually after verifying the file tree.

---

## After Copilot finishes — operator instructions

Once Copilot confirms all operations are complete and you have eye-checked the file tree:

**1. Spot-check by eye** — open at least three READMEs at different depths to verify content is intact. Especially look at:
- `backend/README.md` (the architecture summary table)
- `backend/core/README.md` (the dependency rule explanation)
- `frontend/README.md`

**2. Stage and commit:**
```
git add .
git commit -m "Chunk B — folder scaffold: backend, frontend, infra with README anchors"
```

**3. Push:**
```
git push
```

---

## What to verify before moving to Chunk C

- [ ] `backend/` exists with all 12+ subfolders, each containing a README.
- [ ] `frontend/` exists with 7 subfolders, each containing a README.
- [ ] `infra/` exists with 4 subfolders, each containing a README.
- [ ] `output/` exists with its README (and only its README — nothing else).
- [ ] `chunks/chunk_b_folder_scaffold.md` exists.
- [ ] No source code files were created.
- [ ] No package manager files were created.
- [ ] `git status` shows a clean working tree after the commit.
- [ ] `git log` shows two commits: Chunk A and Chunk B.

When all boxes are checked, come back and we plan Chunk C — Python environment setup (`pyproject.toml`, virtual environment, dev dependencies, `__init__.py` files where needed).
