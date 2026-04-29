# Image Generation Providers

Adapters for AI image generation services. Used for thumbnails, channel art, and any still-image needs.

## Status

Not used in Phase 0-3 MVP. Folder exists as a placeholder for the architecture.

## Interface (concept)

```python
class ImageGenerationProvider:
    async def generate(prompt, params) -> ImageResult
```
