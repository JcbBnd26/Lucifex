# Integration Tests

Tests of multiple components working together with real infrastructure (database, file storage).

## Conventions

- Real database, but isolated per test (transactions rolled back, or per-test schema).
- Real file storage if needed (use a test bucket or local equivalent).
- External APIs are still mocked — we don't hit Kling or YouTube in tests.
- Slower than unit tests; fewer in number.
