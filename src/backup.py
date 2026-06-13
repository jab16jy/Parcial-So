"""Backup System module.

Recursively copy files from a source directory to a timestamped
destination folder with a Rich progress bar and a log file.
"""

import shutil
from datetime import datetime
from pathlib import Path

from rich.prompt import Prompt
from rich.progress import Progress

from utils.helpers import console, error_handler, log_event


@error_handler
def run_backup(source: str | Path, dest: str | Path) -> dict:
    """Recursively copy all files from *source* to a timestamped folder under *dest*.

    A log file named ``backup_YYYYMMDD_HHMMSS.log`` is written inside the
    destination folder.

    Args:
        source: Path to the directory to back up.
        dest:   Parent directory where the timestamped backup folder is created.

    Returns:
        Summary dict with keys: status, files_copied, dest_path, log_path.
    """
    src_path = Path(source)
    dest_parent = Path(dest)

    if not src_path.exists():
        console.print(f"[error]Source directory not found: {src_path}[/error]")
        log_event("backup_failed", {"source": str(src_path), "reason": "not_found"})
        return {"status": "error", "reason": "source_not_found", "files_copied": 0}

    if not src_path.is_dir():
        console.print(f"[error]Source is not a directory: {src_path}[/error]")
        return {"status": "error", "reason": "not_a_directory", "files_copied": 0}

    # Create timestamped destination
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = dest_parent / f"backup_{timestamp}"

    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        console.print(f"[error]Cannot create destination: {backup_dir} — Permission denied[/error]")
        log_event("backup_failed", {"dest": str(backup_dir), "reason": "permission_denied"})
        return {"status": "error", "reason": "dest_permission_denied", "files_copied": 0}

    # Collect all files to copy
    all_files: list[Path] = []
    for item in src_path.rglob("*"):
        if item.is_file():
            all_files.append(item)

    if not all_files:
        console.print("[warning]Source directory is empty — 0 files to copy[/warning]")
        # Still write the log
        _write_backup_log(backup_dir, src_path, 0, timestamp)
        log_event("backup_completed", {
            "source": str(src_path),
            "dest": str(backup_dir),
            "files_copied": 0,
        })
        return {"status": "ok", "files_copied": 0, "dest_path": str(backup_dir)}

    # Copy with progress
    copied = 0
    skipped = 0
    with Progress() as progress:
        task = progress.add_task(
            "[cyan]Backing up files...", total=len(all_files)
        )

        for file_path in all_files:
            rel_path = file_path.relative_to(src_path)
            dest_path = backup_dir / rel_path

            try:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)
                copied += 1
            except PermissionError:
                console.print(
                    f"[warning]Permission denied: {rel_path} — skipping[/warning]"
                )
                skipped += 1
            except OSError as e:
                console.print(
                    f"[warning]Could not copy {rel_path}: {e} — skipping[/warning]"
                )
                skipped += 1

            progress.advance(task)

    # Write log file
    log_path = _write_backup_log(backup_dir, src_path, copied, timestamp)

    console.print(f"[success]Backup completed: {copied} files copied to {backup_dir}[/success]")
    if skipped:
        console.print(f"[warning]{skipped} files skipped due to errors[/warning]")

    log_event("backup_completed", {
        "source": str(src_path),
        "dest": str(backup_dir),
        "files_copied": copied,
        "files_skipped": skipped,
    })

    return {
        "status": "ok",
        "files_copied": copied,
        "files_skipped": skipped,
        "dest_path": str(backup_dir),
        "log_path": str(log_path),
    }


def _write_backup_log(backup_dir: Path, source: Path, file_count: int, timestamp: str) -> Path:
    """Write a backup log file inside *backup_dir*.

    Args:
        backup_dir: Destination backup folder.
        source:     Original source path.
        file_count: Number of files copied.
        timestamp:  Timestamp string used in the folder name.

    Returns:
        Path to the created log file.
    """
    log_path = backup_dir / f"backup_{timestamp}.log"
    now = datetime.now()
    lines = [
        f"Backup completed: {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Source: {source}",
        f"Destination: {backup_dir}",
        f"Files copied: {file_count}",
        "Status: OK",
    ]
    try:
        log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        console.print(f"[info]Log written: {log_path}[/info]")
    except OSError as e:
        console.print(f"[warning]Could not write log file: {e}[/warning]")

    return log_path
