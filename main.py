#!/usr/bin/env python3
"""SysAdmin Assistant — entry point.

A Rich-themed CLI tool for OS system administration: monitoring,
process management, file organisation, backups, reports, and
scheduled automation.
"""

import sys
from pathlib import Path

from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align

# Ensure project root is on sys.path so that ``from src.…`` imports work
# even when running from a different CWD.
_project_root = Path(__file__).resolve().parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from utils.helpers import console
from src.scheduler import start_scheduler_thread


def show_menu_header() -> None:
    """Print the application banner."""
    header = (
        "[bold cyan]SYSADMIN ASSISTANT[/bold cyan]\n"
        "[yellow]Sistema de Automatización y Monitoreo[/yellow]"
    )
    console.print()
    console.print(
        Align.center(Panel(header, width=48, border_style="cyan"))
    )


def show_menu() -> None:
    """Print the main menu options."""
    console.print()
    menu_lines = [
        "[bold cyan]1.[/bold cyan] Información del Sistema",
        "[bold cyan]2.[/bold cyan] Monitor de Procesos",
        "[bold cyan]3.[/bold cyan] Organizador de Archivos",
        "[bold cyan]4.[/bold cyan] Copias de Seguridad",
        "[bold cyan]5.[/bold cyan] Generar Reportes",
        "[bold cyan]6.[/bold cyan] Automatización Programada",
        "[bold red]0.[/bold red] Salir",
    ]
    for line in menu_lines:
        console.print(line)
    console.print()


def main() -> None:
    """Run the main application loop."""
    # Ensure runtime directories exist
    Path("logs").mkdir(parents=True, exist_ok=True)
    Path("reports").mkdir(parents=True, exist_ok=True)

    # Start the background scheduler thread
    start_scheduler_thread()

    while True:
        console.clear()
        show_menu_header()
        show_menu()

        try:
            choice = Prompt.ask("[cyan]Seleccione una opción[/cyan]", default="0")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Saliendo...[/yellow]")
            break

        console.clear()

        if choice == "1":
            from src.system_info import display_system_info
            display_system_info()

        elif choice == "2":
            from src.process_monitor import process_monitor_menu
            process_monitor_menu()

        elif choice == "3":
            from src.file_organizer import organize_folder
            folder = Prompt.ask("[cyan]Ruta del directorio a organizar[/cyan]")
            organize_folder(folder)

        elif choice == "4":
            from src.backup import run_backup
            source = Prompt.ask("[cyan]Directorio origen[/cyan]")
            dest = Prompt.ask("[cyan]Directorio destino[/cyan]")
            run_backup(source, dest)

        elif choice == "5":
            from src.report_generator import generate_report
            generate_report()

        elif choice == "6":
            from src.scheduler import scheduler_menu
            scheduler_menu()

        elif choice == "0":
            console.print("[yellow]¡Hasta luego![/yellow]")
            break

        else:
            console.print("[error]Opción inválida[/error]")

        if choice != "0":
            Prompt.ask("\n[dim]Presione Enter para continuar...[/dim]")

    # Flush events log
    from utils.helpers import log_event
    log_event("app_exit", {"status": "ok"})


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Saliendo...[/yellow]")
        sys.exit(0)
