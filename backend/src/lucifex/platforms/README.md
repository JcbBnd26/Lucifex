# Platforms

Adapters for content distribution platforms. Same pattern as `providers/`, different domain.

## The pattern

Each platform (TikTok, YouTube, Instagram, Facebook) implements a common `PostingPlatform` interface. The interface to the rest of the system is uniform: `platform.post(render, caption, schedule_time) -> PostResult`. Internally, each adapter handles its own API quirks, OAuth flow, rate limits, and error handling.

## Structure

- `base.py` — the `PostingPlatform` interface
- `youtube.py` — YouTube adapter (Phase 3 anchor — see DEC-009)
- `tiktok.py` — TikTok adapter (Phase 4)
- `instagram.py` — Instagram adapter (Phase 4)
- `facebook.py` — Facebook adapter (Phase 4)
- `registry.py` — maps platform names from the database to concrete implementations

## OAuth

Each adapter owns its OAuth dance independently. Tokens are stored encrypted in the `platforms` database table.

## See also

- `docs/decision_log.md` — DEC-009 (YouTube as Phase 3 anchor)
