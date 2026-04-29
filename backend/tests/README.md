# Tests

The safety net.

## Structure

Mirrors the backend structure:

- `unit/` — fast, isolated tests of individual functions. Most tests should be these.
- `integration/` — tests of pieces working together with a real database.
- `e2e/` — end-to-end tests of full flows through the API. Slowest, fewest.

## The testing pyramid

Many unit tests, fewer integration tests, very few E2E tests. Inverting this leads to slow, flaky, hard-to-debug test suites.

## What gets tested

Phase 0 ships with one E2E test (login works). Subsequent phases add tests for the new code they introduce. The discipline is: every non-trivial function in `core/` gets unit tests. Adapters get integration tests with mocked external APIs. Critical user flows get E2E tests.
