"""Plugin package loader for the Refer & Earn Bot.

This module dynamically imports all .py files inside the plugins directory
and calls their `register(app)` function if present.
"""

import importlib
import logging
import traceback
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)
LOGGER.info("📦 Plugins package initialized")


def register_all(app: Any) -> int:
    """
    Import all plugin modules and register their handlers with the given app.
    
    Returns:
        int: Number of plugins successfully registered.
    """
    loaded = 0
    plugin_dir = Path(__file__).parent

    for file in sorted(plugin_dir.glob("*.py")):
        if file.name == "__init__.py":
            continue

        module_name = f"{__name__}.{file.stem}"
        try:
            LOGGER.info("🔄 Importing plugin: %s", file.stem)
            module = importlib.import_module(module_name)
        except Exception:
            LOGGER.error(
                "❌ Failed to import plugin %s\n%s",
                file.stem,
                traceback.format_exc()
            )
            continue

        # If the plugin defines a register() function, call it
        if hasattr(module, "register"):
            try:
                module.register(app)
                loaded += 1
                LOGGER.info("✅ Plugin loaded: %s", file.stem)
            except Exception:
                LOGGER.error(
                    "❌ Error registering plugin %s\n%s",
                    file.stem,
                    traceback.format_exc()
                )
        else:
            LOGGER.warning("⚠️ Plugin %s has no register() function", file.stem)

    LOGGER.info("📦 Plugin loading complete: %d module(s) loaded", loaded)
    return loaded
