
import shutil
import subprocess
from dataclasses import dataclass, field

from .config import read_config, ConfigError
from .paths import HYPRLAND_LUA


@dataclass
class CheckResult:
    """
    Result of a Desklint configuration check.
    """

    config_found: bool = False
    lua_detected: bool = False
    legacy_detected: bool = False
    hyprctl_available: bool = False
    reload_successful: bool = False

    legacy_patterns: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def healthy(self) -> bool:
        """
        Return True when the configuration passed the
        important checks.
        """

        return (
            self.config_found
            and self.lua_detected
            and not self.errors
        )


# Common old hyprlang syntax.
#
# These are only indicators. Desklint should warn rather
# than attempt to automatically convert a configuration.
LEGACY_PATTERNS = (
    "bind =",
    "bindm =",
    #"monitor =",
    "exec =",
    "exec-once =",
    "source =",
    "general {",
    "decoration {",
    "animations {",
    "input {",
    "windowrule =",
    #"workspace =",
)


def check_config() -> CheckResult:
    """
    Perform a complete static configuration check.

    This does not reload Hyprland.
    """

    result = CheckResult()

    if not HYPRLAND_LUA.is_file():
        result.errors.append(
            f"Hyprland Lua config not found: {HYPRLAND_LUA}"
        )
        return result

    result.config_found = True

    try:
        content = read_config()
    except ConfigError as exc:
        result.errors.append(str(exc))
        return result

    check_lua_structure(content, result)
    check_legacy_syntax(content, result)
    check_hyprctl(result)

    return result


def check_lua_structure(
    content: str,
    result: CheckResult,
) -> None:
    """
    Perform lightweight checks for modern Hyprland Lua.

    This intentionally does not validate arbitrary Lua syntax.
    """

    lua_indicators = (
        "hl.config(",
        "hl.bind(",
        "hl.bindm(",
        "hl.monitor",
        "hl.dsp.",
    )

    if any(indicator in content for indicator in lua_indicators):
        result.lua_detected = True
        return

    # A Lua file can technically contain configuration without
    # these particular APIs, so don't immediately classify it
    # as invalid.
    if (
        "local " in content
        or "require(" in content
        or "--" in content
    ):
        result.lua_detected = True
        result.warnings.append(
            "Lua detected, but no common Hyprland Lua API "
            "calls were found."
        )
        return

    result.warnings.append(
        "Could not identify modern Hyprland Lua API usage."
    )


def check_legacy_syntax(
    content: str,
    result: CheckResult,
) -> None:
    """
    Look for common legacy hyprlang configuration syntax.
    """

    found = []

    for pattern in LEGACY_PATTERNS:
        if pattern in content:
            found.append(pattern)

    if not found:
        return

    result.legacy_detected = True
    result.legacy_patterns = found

    result.warnings.append(
        "Legacy hyprlang syntax detected."
    )


def check_hyprctl(result: CheckResult) -> None:
    """
    Check whether hyprctl is available.
    """

    if shutil.which("hyprctl") is not None:
        result.hyprctl_available = True
    else:
        result.warnings.append(
            "hyprctl was not found in PATH."
        )


def reload_hyprland() -> tuple[bool, str]:
    """
    Ask Hyprland to reload its configuration.

    Returns:
        (success, message)
    """

    if shutil.which("hyprctl") is None:
        return False, "hyprctl was not found in PATH."

    try:
        process = subprocess.run(
            ["hyprctl", "reload"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        return False, "hyprctl reload timed out."

    except OSError as exc:
        return False, f"Unable to execute hyprctl: {exc}"

    if process.returncode == 0:
        return True, "Hyprland configuration reloaded successfully."

    message = (
        process.stderr.strip()
        or process.stdout.strip()
        or "Hyprland rejected the configuration."
    )

    return False, message


def full_check() -> CheckResult:
    """
    Run static checks and then ask Hyprland to reload.

    The reload is the final runtime validation step.
    """

    result = check_config()

    if not result.config_found:
        return result

    if result.errors:
        return result

    if not result.hyprctl_available:
        return result

    success, message = reload_hyprland()

    result.reload_successful = success

    if success:
        return result

    result.errors.append(message)

    return result
