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
