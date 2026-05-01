"""Typed application configuration.

See `lucifex.config.settings.Settings` for the full list of supported
environment variables. Use `get_settings()` to retrieve the cached
instance.
"""

from lucifex.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
