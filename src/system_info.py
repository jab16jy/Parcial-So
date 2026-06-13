"""System Information module.

Provides OS details, hardware specs, and live resource usage
displayed via Rich panels and tables.
"""

import os
import platform
import socket

import psutil
import shutil
from rich.panel import Panel
from rich.table import Table

from utils.helpers import console, fmt_bytes, error_handler, log_event


def get_system_info() -> dict:
    """Collect operating system and network information.

    Returns:
        Dictionary with keys: hostname, user, os, os_version, architecture, ip.
    """
    info = {
        "hostname": socket.gethostname(),
        "user": os.environ.get("USER") or os.environ.get("USERNAME") or "N/A",
        "os": platform.system(),
        "os_version": "N/A",
        "architecture": platform.machine(),
        "ip": "N/A",
    }

    try:
        info["os_version"] = platform.version()
    except Exception:
        info["os_version"] = "N/A"

    try:
        # Get the non-loopback IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))
        info["ip"] = s.getsockname()[0]
        s.close()
    except Exception:
        info["ip"] = "N/A"

    return info


def get_hardware_info() -> dict:
    """Collect hardware resource metrics (RAM, CPU, disk).

    Returns:
        Dictionary with keys: ram_total, ram_used, ram_free, ram_percent,
        cpu_percent, disk_total, disk_used, disk_free, disk_percent.
    """
    hw: dict = {
        "ram_total": 0,
        "ram_used": 0,
        "ram_free": 0,
        "ram_percent": 0.0,
        "cpu_percent": 0.0,
        "cpu_cores_physical": 0,
        "cpu_cores_logical": 0,
        "disk_total": 0,
        "disk_used": 0,
        "disk_free": 0,
        "disk_percent": 0.0,
    }

    # RAM
    try:
        mem = psutil.virtual_memory()
        hw["ram_total"] = mem.total
        hw["ram_used"] = mem.used
        hw["ram_free"] = mem.free
        hw["ram_percent"] = mem.percent
    except Exception:
        console.print("[warning]Could not read RAM information — permission denied[/warning]")

    # CPU
    try:
        hw["cpu_percent"] = psutil.cpu_percent(interval=0.5)
        hw["cpu_cores_physical"] = psutil.cpu_count(logical=False) or 0
        hw["cpu_cores_logical"] = psutil.cpu_count(logical=True) or 0
    except Exception:
        console.print("[warning]Could not read CPU information[/warning]")

    # Disk
    try:
        usage = psutil.disk_usage("/")
        hw["disk_total"] = usage.total
        hw["disk_used"] = usage.used
        hw["disk_free"] = usage.free
        hw["disk_percent"] = usage.percent
    except Exception:
        console.print("[warning]Could not read disk information — permission denied[/warning]")

    return hw


@error_handler
def display_system_info() -> None:
    """Display system and hardware information using Rich panels and tables."""
    sys_info = get_system_info()
    hw_info = get_hardware_info()

    # -- System info panel --
    sys_lines = (
        f"[bold]Hostname:[/bold] {sys_info['hostname']}\n"
        f"[bold]User:[/bold] {sys_info['user']}\n"
        f"[bold]OS:[/bold] {sys_info['os']}\n"
        f"[bold]Version:[/bold] {sys_info['os_version']}\n"
        f"[bold]Architecture:[/bold] {sys_info['architecture']}\n"
        f"[bold]IP Address:[/bold] {sys_info['ip']}"
    )
    console.print(Panel(sys_lines, title="System Information", border_style="cyan"))

    # -- Hardware resources table --
    table = Table(title="Hardware Resources", border_style="cyan")
    table.add_column("Resource", style="bold cyan")
    table.add_column("Total", style="green")
    table.add_column("Used", style="yellow")
    table.add_column("Free", style="green")
    table.add_column("Usage", style="magenta")

    table.add_row(
        "RAM",
        fmt_bytes(hw_info["ram_total"]),
        fmt_bytes(hw_info["ram_used"]),
        fmt_bytes(hw_info["ram_free"]),
        f"{hw_info['ram_percent']:.1f}%",
    )
    table.add_row(
        "CPU",
        f"{hw_info['cpu_cores_physical']} phys / {hw_info['cpu_cores_logical']} log",
        "",
        "",
        f"{hw_info['cpu_percent']:.1f}%",
    )
    table.add_row(
        "Disk",
        fmt_bytes(hw_info["disk_total"]),
        fmt_bytes(hw_info["disk_used"]),
        fmt_bytes(hw_info["disk_free"]),
        f"{hw_info['disk_percent']:.1f}%",
    )

    console.print(table)

    log_event("view_system_info", {
        "os": sys_info["os"],
        "hostname": sys_info["hostname"],
        "ram_percent": hw_info["ram_percent"],
        "cpu_percent": hw_info["cpu_percent"],
        "disk_percent": hw_info["disk_percent"],
    })
