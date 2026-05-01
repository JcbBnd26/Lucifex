# API Layer

HTTP endpoints exposed to the outside world. The frontend calls these. External integrations may eventually call these.

## What lives here

- Route definitions (organized by domain — `routes/clips.py`, `routes/campaigns.py`, etc.)
- Request validation (Pydantic schemas)
- Response formatting
- HTTP-specific concerns (status codes, headers, CORS)

## What does NOT live here

- Business logic. This layer is *transport*, not logic. An endpoint should parse the request, call a function in `core/`, and format the response. Twenty lines per endpoint. If the endpoint is doing math, calling external services, or making decisions, that work belongs in `core/`.
