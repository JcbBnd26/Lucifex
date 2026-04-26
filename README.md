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
