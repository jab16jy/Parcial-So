"""Shared utilities for the SysAdmin Assistant.

Provides a shared Rich console instance, byte formatting,
error handling decorator, and event logging.
"""

import functools
import json
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.theme import Theme

# Shared Rich console with a dark theme
console = Console(theme=Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red",
    "success": "green",
}))

# Paths for runtime directories — created on first use if missing
LOGS_DIR = Path("logs")
REPORTS_DIR = Path("reports")
EVENTS_LOG = LOGS_DIR / "sysadmin_events.json"


def fmt_bytes(n: int | float) -> str:
    """Convert a byte count to a human-readable string (KB, MB, GB, TB).

    Args:
        n: Number of bytes.

    Returns:
        Formatted string like "12.34 MB" or "1.00 GB".
    """
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024.0:
            return f"{n:.2f} {unit}"
        n /= 1024.0
    return f"{n:.2f} PB"


def error_handler(func):
    """Decorator that catches exceptions and displays them via the shared console.

    The decorated function will return None on failure instead of crashing.

    Args:
        func: The callable to wrap.

    Returns:
        Wrapped function with error handling.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            console.print(f"[error]Error in {func.__name__}: {e}[/error]")
            return None
    return wrapper


def log_event(action: str, details: dict | str, log_file: str | Path = EVENTS_LOG) -> None:
    """Append a timestamped JSON event to the log file.

    Creates the logs directory and log file if they do not exist.

    Args:
        action: Short label for the event (e.g. "backup_run", "process_kill").
        details: Extra data to store (dict or string).
        log_file: Path to the JSON event log.
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    events: list[dict] = []
    if log_path.exists() and log_path.stat().st_size > 0:
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                events = json.load(f)
        except (json.JSONDecodeError, OSError):
            events = []

    events.append({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
    })

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
