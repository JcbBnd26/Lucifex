# Video Generation Providers

Adapters for AI video generation services. Each implements the `VideoGenerationProvider` interface from `../base.py`.

## Planned providers

- `kling.py` — Kling AI (default for Phase 1)
- `runway.py` — Runway
- `veo.py` — Google Veo
- `sora.py` — OpenAI Sora
- `grok.py` — xAI video generation

## Interface (concept)

```python
class VideoGenerationProvider:
    async def generate(prompt, params) -> GenerationJob
    async def get_status(job_id) -> JobStatus
    async def get_result(job_id) -> VideoResult
```

Generation is asynchronous on every provider — the adapter abstracts the polling, webhook, or callback pattern into a uniform job-based interface.
