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
