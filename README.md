# SysAdmin Assistant

CLI tool for OS system administration tasks — system monitoring, process
management, file organisation, backups, reports, and scheduled automation.

Built for the Operating Systems course at university.

## Requirements

- Python 3.10+
- pip

## Dependencies

Install with:

```bash
pip install -r requirements.txt
```

- **psutil** — system and process metrics
- **rich** — beautiful CLI output (tables, panels, progress bars)
- **schedule** — periodic task scheduling

## How to Run

```bash
python main.py
```

## Modules

| # | Module | Description |
|---|--------|-------------|
| 1 | System Information | OS details, hardware specs, live resource usage |
| 2 | Process Monitor | List, search, and kill processes with system-PID protection |
| 3 | File Organizer | Auto-categorise files by type (Documents, Images, Videos, Others) |
| 4 | Backup System | Recursive copy with progress bar and timestamped logs |
| 5 | Report Generator | Export system info + process list to TXT or CSV |
| 6 | Scheduled Automation | Schedule backup/report/organise tasks at set intervals |

## Safety

- PID 0 and PID 1 are **always protected** from termination.
- Root-owned processes require **extra confirmation** before killing.
- All operations are logged to `logs/sysadmin_events.json`.
