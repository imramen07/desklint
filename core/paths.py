
from pathlib import Path
import os


# ─────────────────────────────────────────────
# Base configuration directory
# ─────────────────────────────────────────────

XDG_CONFIG_HOME = Path(
    os.environ.get(
        "XDG_CONFIG_HOME",
        Path.home() / ".config",
    )
)


# ─────────────────────────────────────────────
# Hyprland
# ─────────────────────────────────────────────

HYPRLAND_DIR = XDG_CONFIG_HOME / "hypr"

HYPRLAND_LUA = HYPRLAND_DIR / "hyprland.lua"


# ─────────────────────────────────────────────
# Desklint
# ─────────────────────────────────────────────

DESKLINT_DIR = HYPRLAND_DIR / "desklint"

BACKUP_DIR = DESKLINT_DIR / "backups"


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def ensure_desklint_dirs() -> None:
    """Create Desklint's directories if they don't exist."""
    DESKLINT_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def config_exists() -> bool:
    """Return True if the modern Hyprland Lua config exists."""
    return HYPRLAND_LUA.is_file()
