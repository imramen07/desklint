
from pathlib import Path

from .paths import HYPRLAND_LUA, config_exists


class ConfigError(Exception):
    """Raised when a Hyprland configuration operation fails."""


def read_config() -> str:
    """
    Read the current Hyprland Lua configuration.

    Returns:
        The complete configuration as a string.

    Raises:
        ConfigError: If the configuration does not exist
                     or cannot be read.
    """
    if not config_exists():
        raise ConfigError(
            f"Hyprland Lua config not found: {HYPRLAND_LUA}"
        )

    try:
        return HYPRLAND_LUA.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(
            f"Unable to read {HYPRLAND_LUA}: {exc}"
        ) from exc


def write_config(content: str) -> None:
    """
    Replace the Hyprland Lua configuration with new content.

    Args:
        content: Complete configuration text.

    Raises:
        ConfigError: If the configuration cannot be written.
    """
    try:
        HYPRLAND_LUA.write_text(
            content,
            encoding="utf-8",
        )
    except OSError as exc:
        raise ConfigError(
            f"Unable to write {HYPRLAND_LUA}: {exc}"
        ) from exc


def config_size() -> int:
    """
    Return the configuration size in bytes.

    Raises:
        ConfigError: If the configuration does not exist.
    """
    if not config_exists():
        raise ConfigError(
            f"Hyprland Lua config not found: {HYPRLAND_LUA}"
        )

    try:
        return HYPRLAND_LUA.stat().st_size
    except OSError as exc:
        raise ConfigError(
            f"Unable to inspect {HYPRLAND_LUA}: {exc}"
        ) from exc


def replace_config(old: str, new: str) -> bool:
    """
    Replace the first occurrence of `old` with `new`.

    This is intentionally simple for the MVP. More advanced
    Lua-aware editing can be added later.

    Returns:
        True if a replacement was made.
        False if `old` was not found.

    Raises:
        ConfigError: If the configuration cannot be read/written.
    """
    content = read_config()

    if old not in content:
        return False

    updated = content.replace(old, new, 1)

    write_config(updated)

    return True
