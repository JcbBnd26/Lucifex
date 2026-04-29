# Lib

Utilities and infrastructure used across features.

## What lives here

- `api.ts` — wraps fetch calls to the Lucifex backend
- `auth.ts` — authentication helpers
- `format.ts` — formatting utilities (dates, numbers, currency)
- Custom React hooks that aren't tied to a single feature
- TypeScript type definitions shared across features

## What does NOT live here

Feature-specific code. If a hook is only used in clip review, it lives in `features/clip-review/`, not here.
