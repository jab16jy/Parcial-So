"""Report Generator module.

Export system information, hardware resource usage, and active process
lists to TXT or CSV format files.
"""

import csv
from datetime import datetime
from pathlib import Path

from rich.prompt import Prompt

from utils.helpers import console, error_handler, log_event, REPORTS_DIR


@error_handler
def generate_txt_report(output_dir: str | Path = REPORTS_DIR) -> str | None:
    """Write a formatted plain-text report to a timestamped file.

    Imports ``system_info`` and ``process_monitor`` at call time.

    Args:
        output_dir: Directory where the report will be saved.

    Returns:
        Path to the created report file, or None on failure.
    """
    # Lazy imports to avoid cross-module coupling at load time
    from src.system_info import get_system_info, get_hardware_info
    from src.process_monitor import list_processes

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = out / f"report_{timestamp}.txt"

    sys_info = get_system_info()
    hw_info = get_hardware_info()
    processes = list_processes(sort_by="cpu")[:10]  # Top 10

    lines = [
        "=" * 60,
        "           SYSTEM ADMINISTRATOR REPORT",
        "=" * 60,
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "-" * 60,
        "  1. SYSTEM INFORMATION",
        "-" * 60,
        f"  Hostname:     {sys_info.get('hostname', 'N/A')}",
        f"  User:         {sys_info.get('user', 'N/A')}",
        f"  OS:           {sys_info.get('os', 'N/A')}",
        f"  Version:      {sys_info.get('os_version', 'N/A')}",
        f"  Architecture: {sys_info.get('architecture', 'N/A')}",
        f"  IP Address:   {sys_info.get('ip', 'N/A')}",
        "",
        "-" * 60,
        "  2. HARDWARE RESOURCES",
        "-" * 60,
        "  RAM:",
        f"    Total:    {_safe_fmt(hw_info, 'ram_total')}",
        f"    Used:     {_safe_fmt(hw_info, 'ram_used')}",
        f"    Free:     {_safe_fmt(hw_info, 'ram_free')}",
        f"    Usage:    {hw_info.get('ram_percent', 'N/A')}%",
        "",
        "  CPU:",
        f"    Usage:         {hw_info.get('cpu_percent', 'N/A')}%",
        f"    Physical cores: {hw_info.get('cpu_cores_physical', 'N/A')}",
        f"    Logical cores:  {hw_info.get('cpu_cores_logical', 'N/A')}",
        "",
        "  Disk:",
        f"    Total:    {_safe_fmt(hw_info, 'disk_total')}",
        f"    Used:     {_safe_fmt(hw_info, 'disk_used')}",
        f"    Free:     {_safe_fmt(hw_info, 'disk_free')}",
        f"    Usage:    {hw_info.get('disk_percent', 'N/A')}%",
        "",
        "-" * 60,
        "  3. TOP 10 PROCESSES BY CPU",
        "-" * 60,
    ]

    if processes:
        lines.append(f"  {'PID':>7}  {'NAME':<25}  {'CPU%':>6}  {'MEM%':>6}")
        lines.append(f"  {'-------':>7}  {'-' * 25:25}  {'------':>6}  {'------':>6}")
        for p in processes:
            lines.append(
                f"  {p['pid']:>7}  {p['name']:<25}  {p['cpu_percent']:>6.1f}  {p['memory_percent']:>6.1f}"
            )
    else:
        lines.append("  No processes found.")

    lines.extend([
        "",
        "=" * 60,
        "  END OF REPORT",
        "=" * 60,
        "",
    ])

    try:
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"[success]TXT report saved: {report_path}[/success]")
        log_event("report_generated", {"format": "txt", "path": str(report_path)})
        return str(report_path)
    except (OSError, IOError) as e:
        console.print(f"[error]Cannot write report: Permission denied — {report_path}[/error]")
        log_event("report_failed", {"format": "txt", "reason": str(e)})
        return None


@error_handler
def generate_csv_report(output_dir: str | Path = REPORTS_DIR) -> str | None:
    """Write a CSV report to a timestamped file.

    Imports ``system_info`` and ``process_monitor`` at call time.

    Args:
        output_dir: Directory where the report will be saved.

    Returns:
        Path to the created report file, or None on failure.
    """
    from src.system_info import get_system_info, get_hardware_info
    from src.process_monitor import list_processes

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = out / f"report_{timestamp}.csv"

    sys_info = get_system_info()
    hw_info = get_hardware_info()
    processes = list_processes(sort_by="cpu")[:10]

    try:
        with open(report_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Section: System Info
            writer.writerow(["SECTION", "System Information"])
            writer.writerow(["Hostname", sys_info.get("hostname", "N/A")])
            writer.writerow(["User", sys_info.get("user", "N/A")])
            writer.writerow(["OS", sys_info.get("os", "N/A")])
            writer.writerow(["OS Version", sys_info.get("os_version", "N/A")])
            writer.writerow(["Architecture", sys_info.get("architecture", "N/A")])
            writer.writerow(["IP Address", sys_info.get("ip", "N/A")])
            writer.writerow([])

            # Section: Hardware Resources
            writer.writerow(["SECTION", "Hardware Resources"])
            writer.writerow(["Metric", "Total", "Used", "Free", "Usage%"])
            writer.writerow([
                "RAM",
                _safe_fmt(hw_info, "ram_total"),
                _safe_fmt(hw_info, "ram_used"),
                _safe_fmt(hw_info, "ram_free"),
                hw_info.get("ram_percent", "N/A"),
            ])
            writer.writerow([
                "CPU",
                f"{hw_info.get('cpu_cores_physical', 'N/A')} phys / {hw_info.get('cpu_cores_logical', 'N/A')} log",
                "",
                "",
                hw_info.get("cpu_percent", "N/A"),
            ])
            writer.writerow([
                "Disk",
                _safe_fmt(hw_info, "disk_total"),
                _safe_fmt(hw_info, "disk_used"),
                _safe_fmt(hw_info, "disk_free"),
                hw_info.get("disk_percent", "N/A"),
            ])
            writer.writerow([])

            # Section: Processes
            writer.writerow(["SECTION", f"Top {len(processes)} Processes by CPU"])
            if processes:
                writer.writerow(["PID", "Name", "CPU%", "MEM%"])
                for p in processes:
                    writer.writerow([p["pid"], p["name"], p["cpu_percent"], p["memory_percent"]])
            else:
                writer.writerow(["No processes"])

        console.print(f"[success]CSV report saved: {report_path}[/success]")
        log_event("report_generated", {"format": "csv", "path": str(report_path)})
        return str(report_path)
    except (OSError, IOError) as e:
        console.print(f"[error]Cannot write report: Permission denied — {report_path}[/error]")
        log_event("report_failed", {"format": "csv", "reason": str(e)})
        return None


@error_handler
def generate_report() -> None:
    """Prompt the user for TXT or CSV format and generate the report."""
    choice = Prompt.ask(
        "[cyan]Select report format[/cyan]",
        choices=["txt", "csv", "1", "2"],
        default="txt",
    )

    if choice in ("1", "txt"):
        generate_txt_report()
    elif choice in ("2", "csv"):
        generate_csv_report()


def _safe_fmt(d: dict, key: str) -> str:
    """Return a human-readable byte string for a dict key, or 'N/A'."""
    val = d.get(key, "N/A")
    if isinstance(val, (int, float)):
        from utils.helpers import fmt_bytes
        return fmt_bytes(val)
    return str(val)
