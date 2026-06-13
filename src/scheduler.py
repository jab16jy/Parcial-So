"""Scheduled Automation module.

Schedule, list, and cancel automated backup, report generation,
and file organisation tasks using the ``schedule`` library.
"""

import threading
import time
from datetime import datetime

import schedule as sched
from rich.table import Table
from rich.prompt import Prompt

from utils.helpers import console, error_handler, log_event

# ── Stored paths for automated tasks ──────────────────────────────────
# These are set when the user schedules a task so we can re-use them
# when the job fires without user interaction.
_last_backup_source: str | None = None
_last_backup_dest: str | None = None
_last_report_dir: str | None = None
_last_organize_folder: str | None = None

# Metadata tracking for display and cancellation
_scheduled_task_meta: list[dict] = []

# Next auto-incrementing display ID
_next_id: int = 1


def _scheduler_loop() -> None:
    """Daemon thread target: run pending schedule jobs every second."""
    while True:
        sched.run_pending()
        time.sleep(1)


def start_scheduler_thread() -> None:
    """Start the background scheduler daemon thread."""
    thread = threading.Thread(target=_scheduler_loop, daemon=True)
    thread.start()


# ── Scheduled job runners ────────────────────────────────────────────

def _run_backup_job() -> None:
    """Execute a scheduled backup using stored paths."""
    if not _last_backup_source or not _last_backup_dest:
        console.print("[warning]Backup paths not configured — skipping run[/warning]")
        return
    try:
        from src.backup import run_backup
        summary = run_backup(_last_backup_source, _last_backup_dest)
        count = summary.get("files_copied", 0)
        console.print(f"[info]Scheduled backup complete: {count} files[/info]")
        log_event("scheduled_backup_executed", {
            "source": _last_backup_source,
            "files_copied": count,
        })
    except Exception as e:
        console.print(f"[error]Scheduled backup failed: {e}[/error]")
        log_event("scheduled_backup_failed", {"error": str(e)})


def _run_report_job() -> None:
    """Execute a scheduled report generation using stored paths."""
    from src.report_generator import generate_txt_report
    try:
        path = generate_txt_report(output_dir=_last_report_dir or "reports")
        if path:
            console.print(f"[info]Scheduled report generated: {path}[/info]")
            log_event("scheduled_report_executed", {"path": path})
    except Exception as e:
        console.print(f"[error]Scheduled report failed: {e}[/error]")
        log_event("scheduled_report_failed", {"error": str(e)})


def _run_organize_job() -> None:
    """Execute a scheduled file organisation using stored paths."""
    if not _last_organize_folder:
        console.print("[warning]Organise folder not configured — skipping run[/warning]")
        return
    try:
        from src.file_organizer import organize_folder
        summary = organize_folder(_last_organize_folder)
        count = summary.get("files_moved", 0)
        console.print(f"[info]Scheduled organisation complete: {count} files moved[/info]")
        log_event("scheduled_organize_executed", {
            "folder": _last_organize_folder,
            "files_moved": count,
        })
    except Exception as e:
        console.print(f"[error]Scheduled organisation failed: {e}[/error]")
        log_event("scheduled_organize_failed", {"error": str(e)})


# ── Public scheduling API ────────────────────────────────────────────

def schedule_backup(interval_minutes: int) -> None:
    """Schedule a recurring backup task.

    Args:
        interval_minutes: Interval between runs (in minutes).
    """
    global _next_id
    job = sched.every(interval_minutes).minutes.do(_run_backup_job)
    meta = {
        "id": _next_id,
        "type": "Backup",
        "label": f"Every {interval_minutes} min",
        "job": job,
    }
    _scheduled_task_meta.append(meta)
    _next_id += 1
    console.print(f"[success]Backup scheduled every {interval_minutes} minutes[/success]")
    log_event("scheduler_task_added", {
        "task_type": "backup",
        "interval_minutes": interval_minutes,
    })


def schedule_report(interval_minutes: int) -> None:
    """Schedule a recurring report generation task.

    Args:
        interval_minutes: Interval between runs (in minutes).
    """
    global _next_id
    job = sched.every(interval_minutes).minutes.do(_run_report_job)
    meta = {
        "id": _next_id,
        "type": "Report",
        "label": f"Every {interval_minutes} min",
        "job": job,
    }
    _scheduled_task_meta.append(meta)
    _next_id += 1
    console.print(f"[success]Report scheduled every {interval_minutes} minutes[/success]")
    log_event("scheduler_task_added", {
        "task_type": "report",
        "interval_minutes": interval_minutes,
    })


def schedule_organize(interval_minutes: int) -> None:
    """Schedule a recurring file organisation task.

    Args:
        interval_minutes: Interval between runs (in minutes).
    """
    global _next_id
    job = sched.every(interval_minutes).minutes.do(_run_organize_job)
    meta = {
        "id": _next_id,
        "type": "Organize",
        "label": f"Every {interval_minutes} min",
        "job": job,
    }
    _scheduled_task_meta.append(meta)
    _next_id += 1
    console.print(f"[success]Organize scheduled every {interval_minutes} minutes[/success]")
    log_event("scheduler_task_added", {
        "task_type": "organize",
        "interval_minutes": interval_minutes,
    })


def list_tasks() -> None:
    """Display all currently scheduled tasks in a Rich table."""
    if not _scheduled_task_meta:
        console.print("[warning]No tasks currently scheduled[/warning]")
        return

    table = Table(title="Scheduled Tasks", border_style="cyan")
    table.add_column("#", style="bold yellow", justify="right")
    table.add_column("Type", style="green")
    table.add_column("Interval", style="cyan")
    table.add_column("Next Run", style="magenta")

    for meta in _scheduled_task_meta:
        job = meta["job"]
        next_str = (
            job.next_run.strftime("%Y-%m-%d %H:%M:%S")
            if hasattr(job, "next_run") and job.next_run
            else "N/A"
        )
        table.add_row(str(meta["id"]), meta["type"], meta["label"], next_str)

    console.print(table)


def cancel_task_by_id(task_id: int) -> None:
    """Cancel a scheduled task by its display ID.

    Args:
        task_id: Numeric ID shown in the task list.
    """
    for meta in _scheduled_task_meta:
        if meta["id"] == task_id:
            try:
                sched.cancel_job(meta["job"])
            except Exception:
                pass  # Job may already be cancelled
            _scheduled_task_meta.remove(meta)
            console.print(f"[success]{meta['type']} task #{task_id} has been cancelled[/success]")
            log_event("scheduler_task_cancelled", {
                "task_type": meta["type"],
                "task_id": task_id,
            })
            return

    console.print(f"[error]Task #{task_id} not found[/error]")


# ── Submenu ──────────────────────────────────────────────────────────

def _parse_interval(text: str) -> int | None:
    """Parse a user-provided interval string.

    Accepted formats: ``<number>`` (assumes minutes) or plain integer.

    Args:
        text: Raw input from the user.

    Returns:
        Number of minutes, or None if unparseable.
    """
    text = text.strip().lower()
    # Strip common prefixes
    for prefix in ("every ", "each "):
        if text.startswith(prefix):
            text = text[len(prefix):]

    parts = text.split()
    if not parts:
        return None

    try:
        value = int(parts[0])
    except ValueError:
        return None

    # If a unit is specified, try to respect it
    if len(parts) > 1:
        unit = parts[1]
        if unit.startswith("hour"):
            value *= 60
        elif unit.startswith("min"):
            pass  # already minutes
        elif unit.startswith("sec"):
            value = max(1, value // 60)
        else:
            return None  # unknown unit

    return max(1, value)


@error_handler
def scheduler_menu() -> None:
    """Display the scheduler sub-menu and handle user choices."""
    while True:
        console.print()
        console.print("[bold cyan]╔══ Automatización Programada ══╗[/bold cyan]")
        console.print("[bold cyan]║[/bold cyan] 1. Programar copia de seguridad [bold cyan]║[/bold cyan]")
        console.print("[bold cyan]║[/bold cyan] 2. Programar reporte           [bold cyan]║[/bold cyan]")
        console.print("[bold cyan]║[/bold cyan] 3. Programar organizador       [bold cyan]║[/bold cyan]")
        console.print("[bold cyan]║[/bold cyan] 4. Listar tareas activas      [bold cyan]║[/bold cyan]")
        console.print("[bold cyan]║[/bold cyan] 5. Cancelar tarea              [bold cyan]║[/bold cyan]")
        console.print("[bold cyan]║[/bold cyan] 6. Volver al menú principal    [bold cyan]║[/bold cyan]")
        console.print("[bold cyan]╚═══════════════════════════════╝[/bold cyan]")

        choice = Prompt.ask("[cyan]Seleccione una opción[/cyan]", default="6")

        if choice == "1":
            _schedule_backup_flow()
        elif choice == "2":
            _schedule_report_flow()
        elif choice == "3":
            _schedule_organize_flow()
        elif choice == "4":
            list_tasks()
        elif choice == "5":
            _cancel_task_flow()
        elif choice == "6":
            break
        else:
            console.print("[error]Opción inválida[/error]")


# ── Internal flow helpers ────────────────────────────────────────────

def _schedule_backup_flow() -> None:
    """Prompt for interval and paths, then schedule a backup."""
    global _last_backup_source, _last_backup_dest

    interval_str = Prompt.ask("[cyan]Interval (minutes or 'every N minutes')[/cyan]")
    minutes = _parse_interval(interval_str)
    if minutes is None:
        console.print(f"[error]Invalid interval: {interval_str}. Use format: every N minutes/hours[/error]")
        return

    src = Prompt.ask("[cyan]Source directory[/cyan]")
    dst = Prompt.ask("[cyan]Destination directory[/cyan]")

    _last_backup_source = src
    _last_backup_dest = dst
    schedule_backup(minutes)


def _schedule_report_flow() -> None:
    """Prompt for interval and output directory, then schedule a report."""
    global _last_report_dir

    interval_str = Prompt.ask("[cyan]Interval (minutes or 'every N minutes')[/cyan]")
    minutes = _parse_interval(interval_str)
    if minutes is None:
        console.print(f"[error]Invalid interval: {interval_str}. Use format: every N minutes/hours[/error]")
        return

    output_dir = Prompt.ask("[cyan]Output directory[/cyan]", default="reports")
    _last_report_dir = output_dir
    schedule_report(minutes)


def _schedule_organize_flow() -> None:
    """Prompt for interval and folder path, then schedule organisation."""
    global _last_organize_folder

    interval_str = Prompt.ask("[cyan]Interval (minutes or 'every N minutes')[/cyan]")
    minutes = _parse_interval(interval_str)
    if minutes is None:
        console.print(f"[error]Invalid interval: {interval_str}. Use format: every N minutes/hours[/error]")
        return

    folder = Prompt.ask("[cyan]Folder to organize[/cyan]")
    _last_organize_folder = folder
    schedule_organize(minutes)


def _cancel_task_flow() -> None:
    """Show tasks and prompt for the ID to cancel."""
    if not _scheduled_task_meta:
        console.print("[warning]No tasks to cancel[/warning]")
        return

    list_tasks()
    id_str = Prompt.ask("[cyan]Enter task # to cancel[/cyan]")
    try:
        task_id = int(id_str.strip())
    except ValueError:
        console.print("[error]Invalid task number[/error]")
        return

    cancel_task_by_id(task_id)
