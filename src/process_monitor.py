"""Process Monitor module.

List, search, and terminate processes with protection against
killing critical system processes (PID 1, PID 0, root-owned).
"""

import psutil
from rich.table import Table
from rich.prompt import Prompt, Confirm

from utils.helpers import console, error_handler, log_event

# Protect these PIDs unconditionally
PROTECTED_PIDS = {0, 1}


def list_processes(sort_by: str = "cpu") -> list[dict]:
    """Return a list of running processes with pid, name, cpu%, and memory%.

    Args:
        sort_by: Sort key — "cpu" (default), "memory", or "pid".

    Returns:
        List of dicts with keys: pid, name, cpu_percent, memory_percent.
    """
    processes: list[dict] = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            processes.append({
                "pid": proc.info["pid"],
                "name": proc.info["name"] or "N/A",
                "cpu_percent": proc.info["cpu_percent"] or 0.0,
                "memory_percent": proc.info["memory_percent"] or 0.0,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    sort_key = {
        "cpu": lambda p: p["cpu_percent"],
        "memory": lambda p: p["memory_percent"],
        "pid": lambda p: p["pid"],
    }.get(sort_by, lambda p: p["cpu_percent"])

    processes.sort(key=sort_key, reverse=(sort_by != "pid"))
    return processes


def build_process_table(processes: list[dict], title: str = "Running Processes") -> Table:
    """Build a Rich Table from a list of process dicts.

    Args:
        processes: List of process dicts from list_processes().
        title: Title for the table.

    Returns:
        A Rich Table instance.
    """
    table = Table(title=title, border_style="cyan")
    table.add_column("PID", style="bold yellow", justify="right")
    table.add_column("Name", style="green")
    table.add_column("CPU %", justify="right")
    table.add_column("MEM %", justify="right")

    for p in processes:
        table.add_row(
            str(p["pid"]),
            p["name"],
            f"{p['cpu_percent']:.1f}",
            f"{p['memory_percent']:.1f}",
        )

    return table


@error_handler
def display_processes() -> None:
    """Display all processes in a Rich table sorted by CPU usage descending."""
    processes = list_processes(sort_by="cpu")

    if not processes:
        console.print("[warning]No processes found[/warning]")
        log_event("list_processes", {"count": 0})
        return

    table = build_process_table(processes, title="Top Processes by CPU Usage")
    console.print(table)
    log_event("list_processes", {"count": len(processes)})


@error_handler
def search_process(name: str) -> list[dict]:
    """Filter processes by name (case-insensitive substring match).

    Args:
        name: Search term to match against process names.

    Returns:
        List of matching process dicts.
    """
    all_procs = list_processes(sort_by="pid")
    name_lower = name.lower()
    matches = [p for p in all_procs if name_lower in p["name"].lower()]
    return matches


@error_handler
def display_search() -> None:
    """Prompt for a process name and show matching results."""
    term = Prompt.ask("[cyan]Enter process name to search[/cyan]")
    matches = search_process(term)

    if not matches:
        console.print(f"[warning]No processes matching '{term}' found[/warning]")
        log_event("search_process", {"term": term, "matches": 0})
        return

    table = build_process_table(matches, title=f"Processes matching '{term}'")
    console.print(table)
    log_event("search_process", {"term": term, "matches": len(matches)})


@error_handler
def kill_process(pid: int) -> bool:
    """Terminate a process by PID with confirmation and system-PID protection.

    Protection rules:
      - PID 0 and PID 1 are always rejected.
      - Root-owned processes (uid 0) require extra confirmation.

    Args:
        pid: Process ID to terminate.

    Returns:
        True if the process was killed, False otherwise.
    """
    # --- Protection: known system PIDs ---
    if pid in PROTECTED_PIDS:
        msg = f"Cannot terminate PID {pid}: system-protected process"
        console.print(f"[error]{msg}[/error]")
        log_event("kill_process_blocked", {"pid": pid, "reason": "protected_pid"})
        return False

    # --- Resolve process ---
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        console.print(f"[error]No process with PID {pid} found[/error]")
        log_event("kill_process_failed", {"pid": pid, "reason": "not_found"})
        return False

    proc_name = proc.name() or "Unknown"

    # --- Protection: root-owned processes ---
    try:
        if proc.uids().effective == 0:
            console.print(
                f"[warning]PID {pid} ({proc_name}) is owned by root — "
                f"terminating it may affect system stability[/warning]"
            )
            if not Confirm.ask("[yellow]Are you SURE you want to kill this system process?[/yellow]"):
                console.print("[info]Kill cancelled[/info]")
                return False
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass

    # --- Confirmation ---
    if not Confirm.ask(f"[yellow]Kill process {pid} ({proc_name})?[/yellow]"):
        console.print("[info]Kill cancelled[/info]")
        return False

    # --- Execute ---
    try:
        proc.terminate()
        proc.wait(timeout=3)
        console.print(f"[success]Process {pid} ({proc_name}) terminated[/success]")
        log_event("process_killed", {"pid": pid, "name": proc_name})
        return True
    except psutil.NoSuchProcess:
        console.print(f"[warning]Process {pid} already terminated[/warning]")
        return True
    except psutil.AccessDenied:
        console.print(f"[error]Permission denied: cannot terminate PID {pid}[/error]")
        log_event("kill_process_failed", {"pid": pid, "reason": "access_denied"})
        return False
    except Exception as e:
        console.print(f"[error]Failed to terminate process {pid}: {e}[/error]")
        log_event("kill_process_failed", {"pid": pid, "reason": str(e)})
        return False


@error_handler
def display_kill() -> None:
    """Prompt for a PID, confirm, and execute the kill with protection."""
    pid_str = Prompt.ask("[cyan]Enter PID to terminate[/cyan]")

    try:
        pid = int(pid_str.strip())
    except ValueError:
        console.print("[error]Invalid PID — must be a numeric value[/error]")
        return

    kill_process(pid)


@error_handler
def process_monitor_menu() -> None:
    """Show the process monitor submenu."""
    while True:
        console.print()
        console.print("[bold cyan]╔══ Monitor de Procesos ══╗[/bold cyan]")
        console.print("[bold cyan]║[/bold cyan] 1. Listar procesos        [bold cyan]║[/bold cyan]")
        console.print("[bold cyan]║[/bold cyan] 2. Buscar proceso         [bold cyan]║[/bold cyan]")
        console.print("[bold cyan]║[/bold cyan] 3. Matar proceso          [bold cyan]║[/bold cyan]")
        console.print("[bold cyan]║[/bold cyan] 4. Volver al menú principal [bold cyan]║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════╝[/bold cyan]")

        choice = Prompt.ask("[cyan]Seleccione una opción[/cyan]", default="4")

        if choice == "1":
            display_processes()
        elif choice == "2":
            display_search()
        elif choice == "3":
            display_kill()
        elif choice == "4":
            break
        else:
            console.print("[error]Opción inválida[/error]")
