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
