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
