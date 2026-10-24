
from datetime import datetime
from pathlib import Path
import shutil

from .paths import (
    HYPRLAND_LUA,
    BACKUP_DIR,
    ensure_desklint_dirs,
    config_exists,
)


class BackupError(Exception):
    """Raised when a backup operation fails."""


def create_backup() -> Path:
    """
    Create a timestamped backup of hyprland.lua.

    Returns:
        Path to the newly created backup.

    Raises:
        BackupError: If the configuration does not exist
                     or the backup cannot be created.
    """

    if not config_exists():
        raise BackupError(
            f"Hyprland Lua config not found: {HYPRLAND_LUA}"
        )

    ensure_desklint_dirs()

    timestamp = datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )

    backup_path = (
        BACKUP_DIR /
        f"hyprland-{timestamp}.lua"
    )

    # Avoid accidentally overwriting a backup if two
    # backups happen within the same second.
    counter = 1

    while backup_path.exists():
        backup_path = (
            BACKUP_DIR /
            f"hyprland-{timestamp}-{counter}.lua"
        )
        counter += 1

    try:
        shutil.copy2(
            HYPRLAND_LUA,
            backup_path,
        )
    except OSError as exc:
        raise BackupError(
            f"Unable to create backup: {exc}"
        ) from exc

    return backup_path


def list_backups() -> list[Path]:
    """
    Return all Desklint backups, newest first.
    """

    if not BACKUP_DIR.exists():
        return []

    backups = list(
        BACKUP_DIR.glob("hyprland-*.lua")
    )

    return sorted(
        backups,
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def latest_backup() -> Path | None:
    """
    Return the newest backup.

    Returns:
        Path to the newest backup, or None if no backups exist.
    """

    backups = list_backups()

    if not backups:
        return None

    return backups[0]


def restore_backup(
    backup_path: Path | None = None,
) -> Path:
    """
    Restore a backup over the current hyprland.lua.

    If backup_path is omitted, the newest backup is restored.

    Returns:
        Path of the backup that was restored.

    Raises:
        BackupError: If the backup cannot be restored.
    """

    if backup_path is None:
        backup_path = latest_backup()

    if backup_path is None:
        raise BackupError(
            "No Desklint backups are available."
        )

    backup_path = Path(backup_path)

    if not backup_path.is_file():
        raise BackupError(
            f"Backup does not exist: {backup_path}"
        )

    ensure_desklint_dirs()

    # Before overwriting the current configuration, save it.
    if config_exists():
        timestamp = datetime.now().strftime(
            "%Y%m%d-%H%M%S"
        )

        safety_backup = (
            BACKUP_DIR /
            f"before-rollback-{timestamp}.lua"
        )

        counter = 1

        while safety_backup.exists():
            safety_backup = (
                BACKUP_DIR /
                f"before-rollback-{timestamp}-{counter}.lua"
            )
            counter += 1

        try:
            shutil.copy2(
                HYPRLAND_LUA,
                safety_backup,
            )
        except OSError as exc:
            raise BackupError(
                f"Unable to create rollback safety backup: {exc}"
            ) from exc

    try:
        shutil.copy2(
            backup_path,
            HYPRLAND_LUA,
        )
    except OSError as exc:
        raise BackupError(
            f"Unable to restore backup: {exc}"
        ) from exc

    return backup_path


def delete_backup(backup_path: Path) -> None:
    """
    Delete a specific backup.

    This is not required by the MVP CLI yet, but keeping the
    operation here makes backup management easier later.
    """

    backup_path = Path(backup_path)

    if not backup_path.is_file():
        raise BackupError(
            f"Backup does not exist: {backup_path}"
        )

    try:
        backup_path.unlink()
    except OSError as exc:
        raise BackupError(
            f"Unable to delete backup: {exc}"
        ) from exc
