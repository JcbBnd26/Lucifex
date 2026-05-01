# Providers

Adapters for external AI services. Where BYOLLM lives.

## The pattern

Each external service (LLM, video generation, image generation, TTS) sits behind a common interface defined in `base.py`. Each concrete provider implements that interface. Code outside `providers/` only ever talks to the abstract interface, never to a concrete provider.

## Structure

- `base.py` — abstract interfaces (`LLMProvider`, `VideoGenerationProvider`, etc.)
- `llm/` — LLM adapters (Anthropic, OpenAI, Google)
- `video_generation/` — video generation adapters (Kling, Runway, Veo, Sora)
- `image_generation/` — image generation adapters
- `tts/` — text-to-speech adapters
- `registry.py` — maps provider names from the database to concrete implementations

## Why this matters

AI tools change rapidly. Hardcoding "we use Kling" means rewriting when Veo surpasses it. The adapter pattern means swapping providers is a configuration change.

## See also

- `docs/decision_log.md` — DEC-003 (Provider-agnostic adapter pattern, BYOLLM)
