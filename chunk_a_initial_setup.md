# Chunk A — Lucifex Initial Setup

You are working in the currently open VS Code workspace, which is the empty root of a project called "Lucifex". Your job in this chunk is to establish the foundational files of the project: a `.gitignore`, a root `README.md`, a `docs/` folder containing the architecture document and decision log, and a `chunks/` folder where this and future chunk prompt documents are stored.

You will not create any Python files. You will not create any source code folders (`backend/`, `frontend/`, `infra/`). Those come in Chunk B. You will not run any git commands. You will not run any other terminal commands except those required to create folders on Windows.

When you are finished, report back with confirmation of each operation and show the final file tree at the project root.

---

## Operation 1 — Create the root `.gitignore`

At the project root, create a file named `.gitignore` with the exact content below.

```
# ============================================================================
# Section 1 — Python
# ============================================================================
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
*.egg
.eggs/
build/
dist/
develop-eggs/
downloads/
parts/
sdist/
wheels/
share/python-wheels/
*.manifest
*.spec
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
.coverage
.coverage.*
htmlcov/
.tox/
.nox/
coverage.xml
*.cover
*.py,cover
.hypothesis/
.ruff_cache/
.mypy_cache/

# ============================================================================
# Section 2 — Virtual environments
# ============================================================================
.venv/
venv/
env/
ENV/
.env
.env.local
.env.*.local

# ============================================================================
# Section 3 — Node / Frontend
# ============================================================================
node_modules/
.next/
out/
dist/
.turbo/
.vercel/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# ============================================================================
# Section 4 — IDE and editor files
# ============================================================================
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# ============================================================================
# Section 5 — Operational outputs
# ============================================================================
output/
!output/README.md
logs/
*.log
tmp/
temp/

# ============================================================================
# Section 6 — Secrets and credentials
# ============================================================================
*.pem
*.key
*.crt
secrets/
credentials/
.secret
.secrets

# ============================================================================
# Section 7 — Database and storage
# ============================================================================
*.sqlite
*.sqlite3
*.db
local_storage/
```

The `!output/README.md` exception in Section 5 is intentional. The `output/` folder will be created in a later chunk, and we want its README tracked so the folder is documented in the repo even though its contents are gitignored.

---

## Operation 2 — Create the root `README.md`

At the project root, create a file named `README.md` with the exact content below.

```
# Lucifex

**Commercial Grade Apps for Personal Use.**

Lucifex is an autonomous content production system. The operator directs strategy through a chat interface; the system generates AI video clips, manages multi-platform distribution, and tracks performance across multiple brand identities. The agent acts on behalf of the operator within configurable bounds.

The name *Lucifex* is a Latin compound: *luci-* (light) + *-fex* (maker), built on the same pattern as *artifex* (art-maker) and *opifex* (work-maker). It means "light-maker."

## Architecture

Lucifex is organized as a decoupled three-region system:

| Region | Purpose |
|--------|---------|
| `backend/` | Python and FastAPI. Business logic, agent loop, database, providers, platforms, workers. |
| `frontend/` | Next.js and React. Dashboard and agent chat interface. |
| `infra/` | Deployment configs, Docker, CI/CD. |

The backend follows hexagonal architecture: dependencies point inward toward `core/`, which holds pure domain logic and depends on nothing else.

For the full architecture and decision history, see:
- [`docs/architecture.md`](docs/architecture.md) — system design, data model, build sequence
- [`docs/decision_log.md`](docs/decision_log.md) — record of consequential architectural decisions

## Sister Project

Lucifex is part of the Project Money portfolio alongside [Nom de Plume](https://github.com/JcbBnd26/Nom-de-plume), which is a production system for AI-authored fiction.

## Status

This project is in initial scaffold. No functional code yet.
```

---

## Operation 3 — Create the `docs/` folder

Create a folder named `docs/` at the project root.

Inside `docs/`, create a file named `README.md` with the exact content below.

```
# Documentation

Project-level documentation for Lucifex.

- `architecture.md` — system design, data model, build phases, architectural patterns
- `decision_log.md` — running record of consequential architectural decisions
```

---

## Operation 4 — Create `docs/architecture.md`

Inside `docs/`, create a file named `architecture.md` with the exact content below. This is the foundational architecture document. It is long. Reproduce the entire content faithfully, including all headings, code blocks, tables, and formatting.

````
# Lucifex — Architecture & Planning Document

**Project:** Lucifex
**Tagline:** Commercial Grade Apps for Personal Use
**Sister project:** Nom de Plume (books)
**Portfolio:** Project Money
**Document version:** v1.0
**Last updated:** 2026-04-26

---

## What Lucifex Is

Lucifex is an autonomous content production system. The operator directs strategy through a chat interface; the system generates AI video clips, manages multi-platform distribution, and tracks performance across multiple brand identities. The agent acts on behalf of the operator within configurable bounds.

The name *Lucifex* is a Latin compound: *luci-* (light) + *-fex* (maker), built on the same pattern as *artifex* (art-maker) and *opifex* (work-maker). It means "light-maker." Video is light. The app makes video. The name describes the product.

The name resonates with *Lucifer* (light-bringer) by design — both names share the *lux* root. The slight transgressive edge is intentional and pairs with Nom de Plume's "operating through constructed identities" theme.

---

## Mission Statement

**Commercial Grade Apps for Personal Use.**

This is the principle that governs every architectural decision. The app is built to commercial software standards — security, scalability, observability, reliability, maintainability — even though there is currently only one user. The discipline of building it right the first time means future-you doesn't rebuild it later.

This is not "build an MVP, throw it away, build the real thing." This is "build the smallest version of the real thing, then expand."

---

## Strategic Posture

**Build vs buy:** Build. No paid orchestration services (Make.com, Zapier). The operator pays Anthropic for AI assistance and accepts standard infrastructure costs (servers, domains, storage, AI APIs). Everything else is built in-house.

**Multi-tenant architecture from day one:** The app is structured as if it could be sold as a SaaS product, even though it won't be. Auth, role-based access, encrypted secrets, audit logs — all present from the start.

**No financial/commercial records ever:** The app tracks operational metrics in dollar terms (API costs, post revenue) because that's performance data. The app does NOT track business operations (LLC records, taxes, invoicing, bookkeeping). Those live in dedicated tools outside the repo.

**Provider-agnostic (BYOLLM):** Every external service (LLM, video generation, posting platforms) sits behind an adapter interface. Swap providers via configuration, not code changes.

---

## The Architecture

### Top-level structure

```
lucifex/
├── backend/      ← Python, FastAPI, business logic, agent, database, workers
├── frontend/     ← Next.js, React, dashboard and chat UI
└── infra/        ← Deployment configs, Docker, CI/CD
```

Backend and frontend are decoupled — they communicate over an API. They could be deployed on different machines, written by different people, even rewritten in different languages without the other knowing. This is the most important architectural decision in modern web apps.

### Backend internal structure

```
backend/
├── api/              ← HTTP endpoints (thin transport layer)
├── core/             ← Pure domain logic, no I/O
├── agent/            ← Agent loop, tools, system prompts
├── db/               ← SQLAlchemy models, Alembic migrations
├── providers/        ← Adapters for AI services (Kling, Veo, Anthropic, etc.)
├── platforms/        ← Adapters for posting platforms (TikTok, YouTube, etc.)
├── workers/          ← Background job runner processes
├── jobs/             ← Job type definitions
├── auth/             ← Authentication, sessions, encryption
├── observability/    ← Logging, metrics, error tracking
├── config/           ← Settings, environment variables
├── tests/            ← Test files mirroring structure
└── main.py           ← Application entry point
```

### Frontend internal structure

```
frontend/
├── app/              ← Next.js routes (pages and layouts)
├── components/       ← Reusable generic UI primitives
├── features/         ← Feature-specific code grouped by domain
├── lib/              ← API client, utilities, hooks
├── styles/           ← Tailwind config, design tokens
├── public/           ← Static assets
└── tests/            ← Frontend tests
```

### Infra internal structure

```
infra/
├── docker/           ← Dockerfiles for backend, frontend, workers
├── deployment/       ← Railway/Fly.io configs
├── github-actions/   ← CI/CD workflows
└── scripts/          ← Operational scripts (backups, seeding, etc.)
```

---

## The Dependency Rule

**Dependencies point inward toward `core/`. Never the reverse.**

- The API layer depends on `core/`.
- Workers depend on `core/`.
- Adapters depend on `core/`.
- `core/` depends on nothing except language primitives and data types.

This makes `core/` the most stable, most reusable, most testable part of the system. The API layer can be swapped for a CLI without touching core. Postgres can be swapped for something else without touching core. The agent's LLM provider can be swapped without touching core.

This pattern is called **Hexagonal Architecture** (also Ports and Adapters or Clean Architecture). It is the prevailing pattern for serious backend systems.

---

## The Tech Stack (Locked In)

**Backend:** Python with FastAPI. Industry-standard for AI-adjacent work, async-native, great for APIs.

**Frontend:** Next.js with React. Commercial-grade defaults, deploys trivially.

**Database:** Postgres, hosted via Supabase or Neon. Generous free tiers, proper backups, can scale.

**Storage:** Cloudflare R2. S3-compatible, no egress fees, dirt cheap.

**Queue:** Postgres-backed jobs (via library like `arq`). Keeps infrastructure simple.

**Hosting:** Railway or Fly.io for backend, Vercel for frontend.

**Observability:** Sentry for errors, Better Stack or Axiom for logs, structlog for structured logging.

**Auth:** Clerk for first version. Drop-in, secure, free for solo use.

**Local development:** VS Code with GitHub Copilot (plan-mode workflow).

**Operating system:** Windows local dev, Linux production.

---

## The Data Model — 20 Tables

### Content production hierarchy

```
channels (brand identities)
  └── concepts (series within a brand)
       └── prompts (scene ideas)
            └── clips (generated videos)
                 └── renders (platform-ready files)
                      └── posts (published instances)
                           └── (optional) campaigns (coordinated push of posts)
```

### The 20 tables

**1. `channels`** — Brand identities. Each row is a brand you operate under (e.g., "Office Capybaras"). Holds voice, visual style, brand rules, target platforms, posting schedule.

**2. `concepts`** — Series within a channel (e.g., "Capybara Small Businesses"). Holds the system prompt that gives the LLM voice for prompt generation in this series.

**3. `prompts`** — Specific scene ideas waiting to be generated. Holds the prompt text and metadata. Tracks `generation_attempt_count`.

**4. `clips`** — Generated AI video files. The actual product coming off the production line. Has `serial_number` (global counter across all clips ever) and `sequence_number_in_concept` (scoped). Tracks provider, cost, duration, status, file location.

**5. `renders`** — Platform-ready versions of approved clips. One render per unique file. Holds `target_platforms` (JSON array — same file can serve multiple platforms when bytes are identical).

**6. `posts`** — Published instances of a render to a platform. One render can become many posts. Tracks `platform_post_id` (the bridge to external state), caption, hashtags, scheduling, performance summary. Has separate `status` (internal) and `platform_state` (external) fields.

**7. `campaigns`** — Coordinated groups of posts treated as a unit. Optional — posts can stand alone. Tracks aggregated metrics for the campaign as a whole.

### Performance

**8. `analytics_snapshots`** — Time-series performance data per post. Append-only. One row per post per pull. Holds raw API response for resilience against platform schema changes.

### External services

**9. `platforms`** — Connected destination accounts (one per platform per channel). Holds encrypted OAuth tokens, refresh tokens, scopes, health status.

**10. `providers`** — AI services configured for use. Holds encrypted API keys, model defaults, cost config, priority, health status. Includes LLM, video generation, image generation, TTS providers.

### Auth and security

**11. `users`** — Human accounts. Holds email, password hash, role, MFA settings, lockout state.

**12. `sessions`** — Active logins. One per device/browser. Token hashes only.

**13. `api_keys`** — Programmatic access keys with scopes. Hashes only.

### System observability

**14. `audit_log`** — Every meaningful action in the system. Append-only. Actor, action, resource, changes (JSON before/after).

**15. `agent_conversations`** — Chat threads with the agent. Tracks total tokens, total cost, system prompt snapshot.

**16. `agent_messages`** — Individual messages within conversations. Holds structured `content_blocks` JSON. Includes per-message `channel_id` for context tracking.

**17. `agent_tool_calls`** — Every tool invocation by the agent. Parameters, results, success, latency, cost.

### Infrastructure

**18. `jobs`** — Background work queue. Holds `idempotency_key` (prevents duplicates), retry state, priority. Status state machine.

**19. `job_runs`** — Execution attempts of jobs. One job can have many runs (initial + retries). Append-only history.

**20. `status_history`** — Polymorphic event log. Every state transition for every state-machine entity (clips, posts, campaigns, renders, jobs). Append-only.

---

## Key Architectural Patterns

**State machines for stateful entities.** Clips, posts, campaigns, renders, and jobs all have explicit status fields with defined valid transitions. Statuses stored as strings with application-level validation (extensible without schema changes).

**Idempotency keys.** Every job has a key derived from its meaning. Prevents duplicate operations from network retries, double-clicks, or restart races. Standard pattern in serious distributed systems.

**Encryption at rest.** OAuth tokens, API keys, MFA secrets — all encrypted in the database, decrypted on read. Encryption key lives in environment variables / secrets manager.

**Hashes over secrets.** Session tokens and API keys are stored as hashes. The actual token only exists in the user's cookie or initial response. Database leak does not equal credential leak.

**Soft deletes.** Tables where deletion matters (clips, posts, prompts) get a `deleted_at` field instead of true row deletion. Append-only tables (analytics_snapshots, audit_log, status_history, agent_messages, job_runs) never delete.

**Denormalization for read performance.** `current_views` on `posts`, `total_views` on `campaigns`, `channel_id` on `clips` — duplicated data that exists for fast queries. Updated by background aggregation jobs. The full history lives in source tables.

**Append-only event logs.** `analytics_snapshots`, `audit_log`, `status_history`, `agent_messages`, `job_runs` are all append-only. History is the asset. Never update, never delete in normal operation.

**Polymorphic event log.** `status_history` holds state transitions for every entity type in one table. Same shape, different `entity_type`. One indexing strategy, one query pattern.

**Adapter pattern for external services.** Every provider (video, LLM, posting) sits behind a common interface. New provider = new module implementing the interface. Code outside the adapter folder never touches concrete providers.

**Separation of internal state from external state.** Posts have `status` (our DB's view) and `platform_state` (the platform's view). They drift independently and that drift is information.

---

## Build Sequence — Walking Skeleton MVP

The smallest version of the real system, exercising every architectural layer end-to-end. Not maximum features, maximum architectural completeness. After MVP, every feature is cheap to add because the layers already exist.

### Phase 0 — Foundation

What gets built:
- Project structure (all folders, scaffolded)
- Database setup (Postgres connected, working)
- Auth scaffolding (users, sessions, login endpoint)
- Config and environment loading
- Logging setup
- Minimal API server that starts
- Minimal frontend that loads
- CI/CD pipeline (push to git → automatic deploy to staging)
- One end-to-end test proving login works

**End state:** You can log in. The deployment pipeline works. Every architectural layer is in place but mostly empty.

### Phase 1 — Manual Generation Flow

What gets built:
- `channels` and `concepts` tables and basic UI
- One video provider adapter (Kling)
- Manual prompt creation
- Clip generation through the system
- Clip review UI
- Cloud storage integration (R2)
- Job queue system (one job type: `generate_video`)
- One worker process

**End state:** You can manually create a prompt, generate a clip, review it, and approve or reject it. No agent, no posting yet.

### Phase 2 — The Agent

What gets built:
- LLM provider adapter (Anthropic)
- Agent loop
- Three tools: `list_pending_review`, `approve_clip`, `generate_video`
- Chat interface in frontend
- Conversation persistence
- Tool call logging

**End state:** You tell the agent "generate 3 clips" and it does. Agent can list and you can approve. Still no posting.

### Phase 3 — Posting

What gets built:
- One platform adapter (YouTube — chosen for documentation quality and lower API friction)
- OAuth flow for connecting YouTube account
- Posting jobs and worker
- Posting tools for the agent (`schedule_post`, `post_immediately`)
- `renders` table fully integrated (passthrough only in MVP)
- Basic analytics pull

**End state:** End-to-end flow works. You direct the agent in chat; it generates, you approve, it posts to YouTube. **MVP complete.**

### Post-MVP Phases

**Phase 4** — Add second platform (TikTok or Instagram). Each new platform = one new adapter following the established pattern.

**Phase 5** — Campaigns table and coordination. Multi-post coordination across platforms.

**Phase 6** — Real analytics dashboard with full `analytics_snapshots` integration. Performance trends, country breakdown, growth curves.

**Phase 7** — API keys table activated. External integrations possible.

**Phase 8+** — Multi-language captions, second video provider, second LLM provider, compilation builder for long-form YouTube, advanced agent capabilities.

---

## Workflow Conventions (Inherited from Nom de Plume)

**Planning vs execution split.** Architectural planning happens in the browser-based Claude conversation. Implementation happens in VS Code with the GitHub Copilot Chat Agent in plan-mode. Plans are captured in markdown documents that the code agent reads (not pasted excerpts).

**Chunked builds.** Each unit of build work is a "chunk" with a written prompt document. Chunks end with a clean git commit naming the chunk.

**Decision log discipline.** Every consequential architectural choice gets a numbered DEC-entry in `docs/decision_log.md` with date, decision, rationale, and revisit conditions.

**Empty folders need README anchors.** Git doesn't track empty folders. Every scaffolded folder gets a README inside, both for git-tracking and as a breadcrumb for future-you about what the folder is for.

**Spot-check high-stakes files by eye.** Especially `.gitignore`, migrations, and anything security-related. Two seconds of eyeballs is cheap insurance.

**Distinguish "no terminal commands" from "no git commands"** in agent prompts. The former is technically wrong on Windows where some operations require shell calls.

---

## Open Questions / Future Decisions

These are deliberately deferred to be answered when the answer matters:

- **Initial niche/concept.** Channel branding (Office Capybaras, etc.) and concept choice deferred until after MVP architecture is built. Test data can be generic.

- **Multi-channel timing.** When to actually run a second channel (after MVP is stable, or earlier as part of MVP testing).

- **Self-hosting vs managed services.** Currently leaning managed (Supabase, Railway, Vercel). Revisit if costs scale or vendor lock-in becomes a concern.

- **CI/CD specifics.** GitHub Actions for sure. Specific deployment workflow design deferred to Phase 0.

- **Agent autonomy bounds.** How much can the agent do without per-action approval? Default to "propose-and-approve" in MVP; relax later as trust is built.

- **Test coverage targets.** Core domain logic gets unit tests from day one. Integration test depth deferred. E2E test design deferred.

---

## Mottos and Principles

**"Aim small, miss small."** Precision in scope. Each chunk is a tight target. Each table change is deliberate. Each phase has a clear endpoint. No spraying across categories.

**"Engine first, content second."** Production infrastructure precedes creative output. Same principle that guides Nom de Plume.

**"Build it once, build it right."** Commercial-grade discipline applied to a personal tool. Pay the discipline tax upfront, save the rebuilding tax later.

---

## Glossary

- **Adapter pattern** — Each external service hides behind a common interface. Code outside the adapter never knows which concrete implementation is running.
- **Append-only** — Table that only accepts inserts, never updates or deletes.
- **BYOLLM** — Bring Your Own LLM. The operator drops in API keys; the app is provider-agnostic.
- **Canto** — Structural unit of a long work, from Dante and Hyperion. Used informally to refer to a single video clip in production planning.
- **Channel** — A brand identity. Each channel has its own voice, brand rules, and posting strategy.
- **Concept** — A content series within a channel.
- **Dependency rule** — Inner layers (core) never depend on outer layers (api, adapters). Dependencies point inward.
- **Hexagonal architecture** — Architectural style where business logic sits at the center, with adapters mediating all external communication.
- **Idempotency key** — A unique identifier on a job that ensures running it multiple times produces the same result as running it once.
- **MVP** — Minimum Viable Product. Here, used in the walking-skeleton sense: smallest version that exercises every architectural layer.
- **Polymorphic event log** — One table holding events about many different entity types, distinguished by an `entity_type` column.
- **Render** — A platform-ready file derived from a clip. One render per unique file.
- **Soft delete** — Marking a row as deleted without actually removing it.
- **State machine** — Entity with explicit valid statuses and defined transitions between them.
- **Walking skeleton** — A system that's complete end-to-end but minimal in every dimension. All layers present, each one thin.

---

## Document Maintenance

This document is the foundation. It is updated when consequential architectural decisions change. Routine implementation details do not belong here — they go in code, comments, or supporting docs.

Updates require:
1. Changing the `Last updated` date at the top.
2. Adding a corresponding DEC-entry in the decision log if the change is consequential.
3. Updating any sections this document references that have changed.

This document does not describe the current *state* of the build — that's tracked in git, the decision log, and chunk documents. This document describes the *intent and shape* of the system.
````

---

## Operation 5 — Create `docs/decision_log.md`

Inside `docs/`, create a file named `decision_log.md` with the exact content below.

```
# Decision Log

A running record of consequential architectural and operational decisions for Lucifex. Every entry is numbered, dated, and structured. Decisions are revisited only when their stated revisit conditions are met.

---

## DEC-001 — Walking-skeleton MVP approach

**Date:** 2026-04-26
**Decision:** Build all architectural layers thinly before fleshing any single layer fully. Phases 0-3 establish the skeleton (foundation, manual generation, agent, posting); Phases 4+ flesh it out with additional platforms, campaigns, analytics dashboards, and other features.
**Rationale:** Building features fully before establishing all layers leads to fragile systems where the first feature works but each subsequent one is harder than it should be. Walking-skeleton ensures every architectural layer ships together, even if thin. After MVP, every additional feature is cheap because the layers already exist.
**Revisit when:** A specific architectural layer proves to need substantial rework before MVP completion. At that point, decide whether to absorb the rework in MVP or defer.

---

## DEC-002 — Commercial-grade from day one

**Date:** 2026-04-26
**Decision:** Despite single-user reality, the app is built to commercial software standards. Auth, encryption at rest, observability, scalability primitives, idempotency, audit logging, and proper deployment pipelines are present from the start.
**Rationale:** "Commercial Grade Apps for Personal Use" is the project's mission statement. Building it right the first time means future-you doesn't rebuild it later. The discipline tax is paid upfront and saves the rebuilding tax later. Many of these primitives also genuinely matter for a single user once the app is internet-facing (every server gets probed within hours of going online).
**Revisit when:** A specific commercial-grade primitive proves to be over-engineering with no current or foreseeable benefit. At that point, document the simplification and the reasoning.

---

## DEC-003 — Provider-agnostic adapter pattern (BYOLLM)

**Date:** 2026-04-26
**Decision:** All external services (LLM, video generation, image generation, TTS, posting platforms) sit behind common adapter interfaces. New providers are added via a new module implementing the interface plus a configuration entry. Code outside the adapter folder never references concrete providers.
**Rationale:** AI tools and platforms change rapidly. Hardcoding specific providers means rewriting when better ones appear. The adapter pattern means swapping providers is a configuration change. Same principle applies to posting platforms — TikTok, YouTube, Instagram, Facebook all sit behind a common interface.
**Revisit when:** A specific provider's interface proves so different from the abstraction that the adapter becomes more complex than separate code paths. At that point, decide whether to extend the abstraction or carve out the special case explicitly.

---

## DEC-004 — No financial or commercial records ever

**Date:** 2026-04-26
**Decision:** Lucifex tracks operational metrics in dollar terms (API costs, post revenue, generation costs, campaign performance) because that is performance data. Lucifex does NOT track business operations (LLC records, EIN, taxes, invoicing, bookkeeping, bank account integration, P&L). Those live in dedicated tools outside this repository.
**Rationale:** Storing actual business records in the same repository as code is a security risk — accidental commits leak sensitive material into git history permanently. Operational metrics that happen to be denominated in dollars (cost per clip, revenue per post) are no more "financial records" than view counts are "audience records." Keeping the boundary clear protects both code and business records.
**Revisit when:** Never under normal circumstances. If business operations need to integrate with the app for any reason, the integration is a one-way export from the app's operational data into the external business tools — not the reverse.

---

## DEC-005 — Hexagonal architecture / dependency rule

**Date:** 2026-04-26
**Decision:** Backend dependencies point inward toward `core/`. The API layer, workers, and adapters depend on `core/`. `core/` depends on nothing except language primitives and data types. Frontend follows an analogous rule (pages depend on features; features depend on components and lib; components and lib depend on nothing else in the project).
**Rationale:** This is the prevailing pattern for serious backend systems (also known as Ports and Adapters or Clean Architecture). It makes `core/` the most stable, most reusable, most testable part of the system. The API can be swapped for a CLI without touching core. Postgres can be swapped without touching core. The agent's LLM can be swapped without touching core.
**Revisit when:** A specific case proves so awkward under the dependency rule that the cost of obeying it exceeds its benefit. Document the exception explicitly rather than silently violating the rule.

---

## DEC-006 — Channels as top of production hierarchy

**Date:** 2026-04-26
**Decision:** The system supports multiple brand identities ("channels"), each with its own voice, brand rules, posting strategy, and target platforms. Concepts (content series) belong to channels. Clips, renders, and posts denormalize `channel_id` for fast querying. The agent loads channel context (voice, brand rules) when operating on behalf of a channel.
**Rationale:** Mirrors Nom de Plume's per-author identity pattern. Without channels, the system can't cleanly separate one brand from another. With channels, each gets its own identity, voice, posting strategy, and analytics rollup. Adding a second channel becomes cheap because all infrastructure is shared; only the channel identity is per-brand.
**Revisit when:** Channels prove insufficient for a use case (e.g., needing sub-channels or cross-channel campaigns). At that point, extend the model deliberately rather than ad hoc.

---

## DEC-007 — One render per unique file

**Date:** 2026-04-26
**Decision:** A render row represents a unique file. If platform output is byte-identical, one render is referenced by multiple posts. If the bytes differ (different captions burned in, different audio, different language), it is a separate render. The `renders.target_platforms` field is a JSON array of platforms a single render can serve.
**Rationale:** Storing data at the level of the thing that varies. The file does not vary per platform when bytes are identical, so platform should not be a property forcing duplication. Platforms vary per post (the act of publishing), so platform identity belongs on posts. Most schema mistakes are violations of this principle.
**Revisit when:** A future requirement forces per-platform variation in every render anyway, making the deduplication moot.

---

## DEC-008 — Postgres + SQLAlchemy + Alembic for the data layer

**Date:** 2026-04-26
**Decision:** The database is Postgres, hosted via Supabase or Neon. Models are defined as SQLAlchemy classes. Schema changes are managed by Alembic migrations, versioned in git, reversible.
**Rationale:** Standard Python data stack. Postgres handles every requirement of the system (relational integrity, JSON fields, indexing at scale, full-text search if needed). SQLAlchemy is the most mature Python ORM. Alembic is the standard migration tool. Migrations versioned in git means schema evolution is reproducible across environments and reversible when something breaks.
**Revisit when:** A specific data requirement proves a poor fit for relational storage (e.g., heavy time-series volume might benefit from a dedicated time-series database). At that point, add the specialized store alongside Postgres rather than replacing it.

---

## DEC-009 — YouTube as Phase 3 anchor platform

**Date:** 2026-04-26
**Decision:** The first posting platform to be implemented is YouTube (specifically YouTube Shorts as the format). Other platforms (TikTok, Instagram, Facebook) come in Phase 4+.
**Rationale:** The goal of Phase 3 is to prove the architecture end-to-end, not to defeat the hardest API. YouTube has the best documentation, the most mature API, and the lowest friction path to a working post. Once one platform works, adding others is a matter of writing more adapters following the established pattern.
**Revisit when:** YouTube's API proves so restrictive that it cannot demonstrate the architecture (e.g., restricted access for AI-generated content). At that point, switch the anchor platform.

---

## DEC-010 — Append-only event logs for history

**Date:** 2026-04-26
**Decision:** The following tables are append-only (insert only, never update, never delete in normal operation): `analytics_snapshots`, `audit_log`, `status_history`, `agent_messages`, `job_runs`. Other tables use soft delete (`deleted_at` field) where deletion is meaningful.
**Rationale:** History is the asset. Knowing a post has 10k views today is useful; knowing it grew from 1k → 5k → 10k → 50k over four days is strategic information. The same applies to audit trails, state transitions, agent conversations, and job execution history. Updating or deleting these rows destroys data that is irreplaceable.
**Revisit when:** Storage costs from append-only tables become non-trivial. At that point, partitioning and archival policies (not deletion) handle the volume.

---

## DEC-011 — String-based extensible enums

**Date:** 2026-04-26
**Decision:** Status fields, provider names, platform names, and similar enumerated values are stored as strings in the database with application-level validation. The valid values live in a configuration file. Adding a new value is a configuration change, not a database migration.
**Rationale:** Hardcoded database enums require migrations to extend, painful when iteration speed matters. String fields with application validation give the same correctness guarantees with no schema friction. Pairs well with the adapter pattern — adding a new provider means adding a string value, not migrating the database.
**Revisit when:** Application-level validation proves to be missed in a code path, leading to invalid values reaching the database. At that point, add stricter enforcement (e.g., database CHECK constraints) rather than reverting to hard enums.

---

## DEC-012 — Idempotency keys on all jobs

**Date:** 2026-04-26
**Decision:** Every job in the queue has an `idempotency_key` field, populated at job creation time, derived from the meaning of the job (e.g., `post_clip_{clip_id}_to_{platform}_{account_id}`). The database enforces uniqueness on this key. Re-creating a job with the same key returns the existing job rather than creating a duplicate.
**Rationale:** This single field prevents an entire category of catastrophic bugs. Network blips, double-clicks, agent retries, and worker restart races can all cause duplicate operations without idempotency. Every serious distributed system uses this pattern (Stripe, AWS, etc.). Building it in from day one is the difference between "works on the happy path" and "works in the real world."
**Revisit when:** Never. This is a foundational pattern.

---
```

---

## Operation 6 — Create the `chunks/` folder

Create a folder named `chunks/` at the project root.

Inside `chunks/`, create a file named `README.md` with the exact content below.

```
# Chunks

Build-step prompt documents for Lucifex. Each chunk is a focused, executable unit of work for the code agent. Chunks are numbered and named.

Chunks are reference material — they are read by the code agent to perform a build step. After execution, they remain in the repository as documentation of how the project was built.

## Convention

- Chunk filenames follow the pattern: `chunk_{letter}_{slug}.md` (e.g., `chunk_a_initial_setup.md`).
- Each chunk is self-contained — the code agent should not need additional context outside the project to execute it.
- Each chunk ends with a git commit naming the chunk.
```

---

## Operation 7 — Save this chunk document

Save this entire chunk document (the file you are currently reading) into the `chunks/` folder as `chunk_a_initial_setup.md`. This preserves the build history.

---

## Constraints

Do not create any other files or folders. Specifically, do not create:
- `backend/`, `frontend/`, `infra/` (these come in Chunk B)
- Any Python files or `pyproject.toml`
- Any frontend config files
- Any source code

Do not run any git commands. Do not run `npm install`, `pip install`, or any package manager. Do not run any terminal commands except those required to create folders on Windows.

Do not modify any existing files except as specified in this document.

---

## When you are finished

Report back with:

1. Confirmation that `.gitignore` exists at the project root with the seven sections.
2. Confirmation that `README.md` exists at the project root with the project overview.
3. Confirmation that `docs/README.md` exists with the documentation index.
4. Confirmation that `docs/architecture.md` exists with the full architecture document.
5. Confirmation that `docs/decision_log.md` exists with twelve DEC entries (DEC-001 through DEC-012).
6. Confirmation that `chunks/README.md` exists with the chunks convention.
7. Confirmation that `chunks/chunk_a_initial_setup.md` exists (this document, saved into the repo).
8. The final file tree at the project root.

Do not stage, commit, or push anything. The operator will run git commands manually after verifying the file tree.

---

## After Copilot finishes — operator instructions

Once Copilot confirms all seven operations are complete, do the following in your VS Code terminal (make sure you are inside the `lucifex/` folder):

**1. Initialize git:**
```
git init
```

**2. Stage all files:**
```
git add .
```

**3. Make the first commit:**
```
git commit -m "Chunk A — initial setup: gitignore, README, architecture doc, decision log, chunks folder"
```

**4. Connect to your GitHub repo (replace with your repo URL):**
```
git remote add origin https://github.com/YOUR_USERNAME/lucifex.git
git branch -M main
git push -u origin main
```

That is your zero-point. From here on, every change is tracked, reversible, and on GitHub.

---

## What to verify before moving to Chunk B

- [ ] `.gitignore` exists at project root with all 7 sections.
- [ ] `README.md` exists at project root with the architecture summary table.
- [ ] `docs/architecture.md` exists and reads correctly start to finish.
- [ ] `docs/decision_log.md` has exactly 12 DEC entries.
- [ ] `chunks/chunk_a_initial_setup.md` exists.
- [ ] `git status` shows a clean working tree.
- [ ] `git log` shows exactly one commit titled "Chunk A — initial setup: ...".
- [ ] The repo is visible on GitHub with all files.

When all eight boxes are checked, come back and we will plan Chunk B — the full backend and frontend folder scaffold.
