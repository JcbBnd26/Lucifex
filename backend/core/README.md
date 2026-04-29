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
