#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from core import (
    BACKUP_DIR,
    HYPRLAND_LUA,
    BackupError,
    ConfigError,
    check_config,
    create_backup,
    full_check,
    list_backups,
    restore_backup,
)


# ─────────────────────────────────────────────
# Output helpers
# ─────────────────────────────────────────────

def info(message: str) -> None:
    print(f"[desklint] {message}")


def success(message: str) -> None:
    print(f"[desklint] ✓ {message}")


def warning(message: str) -> None:
    print(f"[desklint] ⚠ {message}")


def error(message: str) -> None:
    print(f"[desklint] ✗ {message}", file=sys.stderr)


# ─────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────

def command_status() -> int:
    """
    Show the current Desklint configuration status.
    """

    print("Desklint")
    print("========")
    print()

    print("Configuration")
    print(f"  Path: {HYPRLAND_LUA}")

    if HYPRLAND_LUA.is_file():
        success("hyprland.lua found")
    else:
        error("hyprland.lua not found")
        return 1

    print()

    result = check_config()

    print("Checks")

    if result.lua_detected:
        success("Modern Lua configuration detected")
    else:
        warning("Modern Hyprland Lua API not detected")

    if result.legacy_detected:
        warning("Legacy hyprlang syntax detected")
    else:
        success("No obvious legacy syntax detected")

    print()

    print("Hyprland")

    if result.hyprctl_available:
        success("hyprctl available")
    else:
        warning("hyprctl not available")

    print()

    backups = list_backups()

    print("Backups")
    print(f"  Location: {BACKUP_DIR}")
    print(f"  Count:    {len(backups)}")

    if backups:
        print(f"  Latest:   {backups[0].name}")

    return 0


def command_check() -> int:
    """
    Perform a full configuration check and reload Hyprland.
    """

    print("Desklint configuration check")
    print("============================")
    print()

    result = full_check()

    print(f"Config: {HYPRLAND_LUA}")
    print()

    if result.config_found:
        success("Configuration found")
    else:
        error("Configuration not found")

    if result.lua_detected:
        success("Modern Lua configuration detected")
    else:
        warning(
            "Could not confidently identify modern "
            "Hyprland Lua API usage"
        )

    if result.legacy_detected:
        warning("Legacy hyprlang syntax detected")

        for pattern in result.legacy_patterns:
            print(f"    - {pattern}")

    else:
        success("No obvious legacy syntax detected")

    if result.hyprctl_available:
        success("hyprctl available")
    else:
        warning("hyprctl not available")

    print()

    if result.warnings:
        print("Warnings")

        for item in result.warnings:
            print(f"  ⚠ {item}")

        print()

    if result.errors:
        print("Errors")

        for item in result.errors:
            print(f"  ✗ {item}")

        print()
        error("Configuration check failed")
        return 1

    if result.reload_successful:
        success("Hyprland accepted the configuration")
    else:
        warning("Hyprland was not reloaded")

    print()
    success("Configuration check passed")

    return 0


def command_backup() -> int:
    """
    Create a timestamped configuration backup.
    """

    try:
        backup_path = create_backup()
    except BackupError as exc:
        error(str(exc))
        return 1

    success("Backup created")
    print(f"  {backup_path}")

    return 0


def command_backups() -> int:
    """
    List all available backups.
    """

    backups = list_backups()

    print("Desklint backups")
    print("================")
    print()

    if not backups:
        print("No backups found.")
        return 0

    for index, backup in enumerate(backups, start=1):
        size = backup.stat().st_size

        print(
            f"{index:>2}. "
            f"{backup.name} "
            f"({size} bytes)"
        )

    return 0


def command_rollback(backup: str | None) -> int:
    """
    Restore a selected backup or the latest backup.
    """

    selected_backup = None

    if backup:
        selected_backup = Path(backup)

    try:
        restored = restore_backup(selected_backup)

    except BackupError as exc:
        error(str(exc))
        return 1

    success("Configuration restored")
    print(f"  {restored}")

    info(
        "Hyprland has not been reloaded automatically."
    )
    info(
        "Run 'desklint check' to validate and reload."
    )

    return 0


# ─────────────────────────────────────────────
# Argument parser
# ─────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="desklint",
        description=(
            "A lightweight configuration manager "
            "for modern Hyprland Lua configurations."
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version="desklint 0.1.0",
    )

    commands = parser.add_subparsers(
        dest="command",
        metavar="COMMAND",
    )

    commands.add_parser(
        "status",
        help="Show configuration status",
    )

    commands.add_parser(
        "check",
        help="Check and reload the Hyprland configuration",
    )

    commands.add_parser(
        "backup",
        help="Create a configuration backup",
    )

    commands.add_parser(
        "backups",
        help="List available backups",
    )

    rollback_parser = commands.add_parser(
        "rollback",
        help="Restore a configuration backup",
    )

    rollback_parser.add_argument(
        "backup",
        nargs="?",
        help=(
            "Backup file to restore. "
            "Defaults to the latest backup."
        ),
    )

    return parser


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "status":
        return command_status()

    if args.command == "check":
        return command_check()

    if args.command == "backup":
        return command_backup()

    if args.command == "backups":
        return command_backups()

    if args.command == "rollback":
        return command_rollback(args.backup)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())