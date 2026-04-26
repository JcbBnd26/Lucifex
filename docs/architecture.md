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
