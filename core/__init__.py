
"""
Desklint core functionality.

This package contains the filesystem, configuration,
validation, and backup logic used by the Desklint CLI.
"""

from .paths import (
    XDG_CONFIG_HOME,
    HYPRLAND_DIR,
    HYPRLAND_LUA,
    DESKLINT_DIR,
    BACKUP_DIR,
    ensure_desklint_dirs,
    config_exists,
)

from .config import (
    ConfigError,
    read_config,
    write_config,
    config_size,
    replace_config,
)

from .checker import (
    CheckResult,
    check_config,
    full_check,
    reload_hyprland,
)

from .backup import (
    BackupError,
    create_backup,
    list_backups,
    latest_backup,
    restore_backup,
    delete_backup,
)


__all__ = [
    # Paths
    "XDG_CONFIG_HOME",
    "HYPRLAND_DIR",
    "HYPRLAND_LUA",
    "DESKLINT_DIR",
    "BACKUP_DIR",
    "ensure_desklint_dirs",
    "config_exists",

    # Config
    "ConfigError",
    "read_config",
    "write_config",
    "config_size",
    "replace_config",

    # Checker
    "CheckResult",
    "check_config",
    "full_check",
    "reload_hyprland",

    # Backup
    "BackupError",
    "create_backup",
    "list_backups",
    "latest_backup",
    "restore_backup",
    "delete_backup",
]