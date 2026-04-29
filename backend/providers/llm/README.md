# LLM Providers

Adapters for large language model services. Each implements the `LLMProvider` interface from `../base.py`.

## Planned providers

- `anthropic.py` — Claude (default for Phase 2)
- `openai.py` — GPT models
- `google.py` — Gemini models

## Interface (concept)

```python
class LLMProvider:
    async def complete(messages, model, params) -> Completion
    async def complete_with_tools(messages, model, tools, params) -> ToolCallResult
```

Each adapter handles its provider's specific API quirks, authentication, error handling, and response normalization.
