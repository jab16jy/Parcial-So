# Proposal: SysAdmin Assistant

## Intent

Build a Python CLI tool that automates common OS system administration tasks for a university Operating Systems course. The tool replaces manual system monitoring, process management, file organization, and backup workflows with a unified menu-driven interface.

## Scope

### In Scope
- **6 modules**: System Information, Process Monitor, File Organizer, Backup System, Report Generator, Scheduled Automation
- **Extras**: Rich-themed CLI (dark theme default), progress bars (Rich Progress), event logging

### Out of Scope
- GUI or web interface (CLI only)
- Remote/network administration (local machine only)
- Persistent daemon or service installation (user-launched only)

## Capabilities

### New Capabilities
- `system-info`: Display OS, hardware, and resource usage details
- `process-monitor`: List, search, and kill processes with system-process protection
- `file-organizer`: Auto-categorize files by type (Documents, Images, Videos, Others)
- `backup-system`: Copy files from source to destination with timestamped logs
- `report-generator`: Export TXT/CSV reports with system info, resource usage, and active processes
- `scheduled-automation`: Schedule backup, report, and organization tasks via `schedule` library

### Modified Capabilities
None — first iteration, no existing specs.

## Approach

Feature-based architecture: each module is an independent Python module under `src/`. A central menu dispatcher (built with Rich) routes user choices to the correct module. Modules share common utilities (logging, Rich console) but have no cross-dependencies. This keeps development parallelizable and testing straightforward.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/` | New | Module structure: `system_info.py`, `process_monitor.py`, `file_organizer.py`, `backup.py`, `reports.py`, `scheduler.py` |
| `main.py` | New | Entry point with Rich menu loop |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| psutil permission errors on some OS metrics | Medium | Graceful fallbacks with user-friendly messages |
| Killing system processes | Low | Protect PID whitelist (PID 1, system services) |
| Cross-platform path differences | Low | Use `pathlib` for all path operations |

## Rollback Plan

Git revert: `git revert HEAD` if the change introduces issues. Since each module is independent, partial rollbacks via `git checkout` on specific files are also safe.

## Dependencies

- Python 3.10+, psutil, rich, schedule, pathlib (stdlib), shutil (stdlib), datetime (stdlib)

## Success Criteria

- [ ] All 6 modules are functional when run from the main menu
- [ ] Process kill correctly blocks system PIDs
- [ ] File organizer sorts sample files into correct category folders
- [ ] Backup creates destination folder, copies files, and writes a log with date/time/file count
- [ ] Report generation produces readable TXT and CSV output
- [ ] Scheduled automation runs backup/report/organize at set intervals
- [ ] Rich dark theme and progress bars display correctly
