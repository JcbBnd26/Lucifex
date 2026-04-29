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
