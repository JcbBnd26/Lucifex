# Unit Tests

Fast, isolated tests of individual functions and classes.

## Conventions

- No I/O. No database. No network. No filesystem (mock if needed).
- One test file per source file, mirroring the source structure (`tests/unit/core/clips/test_approval.py` tests `core/clips/approval.py`).
- Test names describe what is being verified (`test_clip_cannot_be_approved_when_already_rejected`).
