# Observability

The system observing itself. Logging, errors, metrics, audit log writers, health checks.

## What lives here

- `logging.py` — structured logging configuration (structlog)
- `errors.py` — Sentry integration
- `metrics.py` — performance and business metrics
- `audit.py` — helper functions for writing `audit_log` entries
- `health.py` — health check logic for the API

## Logging philosophy

Logs are data, not text. Every log line is JSON with fields like `level`, `event`, `clip_id`, `error`, `duration_ms`. Structured logs are searchable, filterable, aggregatable. Plain-text logs are not.

## Why a folder, not just imports

Centralizing the configuration (log format, error reporter setup, metrics collectors) means a single source of truth. Every other module in the backend imports `from observability import logger` and gets a properly configured logger.
