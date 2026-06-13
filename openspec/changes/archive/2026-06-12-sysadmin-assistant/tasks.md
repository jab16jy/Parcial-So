# Tasks: SysAdmin Assistant

## Review Workload Forecast

- **Estimated lines**: ~800–1000 (11 files, straightforward logic)
- **400-line budget risk**: High
- **Chained PRs recommended**: No (solo project, single deliverable)
- **Decision needed before apply**: No
- **Delivery strategy**: ask-on-risk

---

## Phase 1: Foundation

- [x] ### Task 1.1 — `requirements.txt`
Dependencies: `psutil`, `rich`, `schedule`.

- [x] ### Task 1.2 — `utils/` package
- `utils/__init__.py` — empty package init
- `utils/helpers.py` — shared Rich console (dark), `fmt_bytes()`, `error_handler` decorator

- [x] ### Task 1.3 — `src/__init__.py`
Empty package init.

---

## Phase 2: Core Modules

- [x] ### Task 2.1 — `src/system_info.py`
OS details via `platform` + `psutil`, hardware specs (CPU cores, RAM, disk), live resource usage (CPU%, memory, disk). Rich panels/table. Graceful "N/A" fallback on permission errors.

- [x] ### Task 2.2 — `src/process_monitor.py`
List all processes (PID, name, CPU%, memory%) sorted by PID; search by name; kill by PID with confirmation. Guard PID 1 (reject) and root-owned processes (warn). Handle non-existent PID.

- [x] ### Task 2.3 — `src/file_organizer.py`
Categorize files: Documents, Images, Videos, Others. Create category dirs, handle duplicates with timestamp suffix. Edge cases: empty/nonexistent dir, permission denied (skip + warn).

- [x] ### Task 2.4 — `src/backup.py`
Recursive copy with Rich Progress. Create destination if missing, abort on permission denied. Write `backup_YYYYMMDD_HHMMSS.log` with source, dest, file count. Handle empty source, merge into existing destination.

- [x] ### Task 2.5 — `src/report_generator.py`
Gather OS, hardware, resource, process data. Export as TXT (`report_YYYYMMDD_HHMMSS.txt`) with section headers and CSV with header + data rows. Handle unavailable data and write failures gracefully.

- [x] ### Task 2.6 — `src/scheduler.py`
Schedule backup/report/organize via `schedule`. Parse "every N minutes/hours". List tasks in Rich table, cancel by selection. Daemon thread loop. Catch task failures without removing job.

---

## Phase 3: Integration

- [x] ### Task 3.1 — `main.py`
Entry point with Rich menu (6 options + exit). Dispatch to each module. Top-level error wrapping. Graceful `KeyboardInterrupt` handling.

- [x] ### Task 3.2 — Smoke test
Verify all modules import and run from menu. Accept paths via `Prompt.ask`.

---

## Phase 4: Polish

- [x] ### Task 4.1 — Progress bars
Rich `Progress` on backup copy and organizer moves.

- [x] ### Task 4.2 — Event logging
JSON log (`sysadmin_events.json`) with timestamped operations.

- [x] ### Task 4.3 — Error handling review
Every module: catch expected errors, display friendly messages, never crash.

- [x] ### Task 4.4 — Docstrings and comments
Module-level docstring, public function docs, inline comments for non-obvious logic.

---

## Implementation Notes

- **No test runner** — manual verification per design.md acceptance table
- **All paths** use `pathlib.Path`; **all output** through shared `utils.helpers.console`
- **Report generator** imports data from system_info + process_monitor at call time
- **Scheduler** stores last-used paths to re-run backup/organize automatically
