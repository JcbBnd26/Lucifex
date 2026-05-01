# Text-to-Speech Providers

Adapters for AI voice synthesis services.

## Status

Not used in Phase 0-3 MVP. Folder exists as a placeholder for the architecture, since voiceovers will likely be needed for long-form YouTube content in later phases.

## Interface (concept)

```python
class TTSProvider:
    async def synthesize(text, voice, params) -> AudioResult
```
