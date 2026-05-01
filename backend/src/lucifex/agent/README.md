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
