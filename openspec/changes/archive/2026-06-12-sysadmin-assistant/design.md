# Design: SysAdmin Assistant

## Technical Approach

Feature-based architecture: 6 independent modules under `src/`, a central Rich menu dispatcher in `main.py`, and a shared `utils/` package for common concerns (console, formatting, error handling). Each module maps 1:1 to a spec — no cross-dependencies between modules. This keeps implementation parallel and testing isolated.

```
main.py ──→ src/system_info.py
         ──→ src/process_monitor.py
         ──→ src/file_organizer.py
         ──→ src/backup.py
         ──→ src/report_generator.py
         ──→ src/scheduler.py
              utils/helpers.py ← shared console, fmt, decorator
```

## Architecture Decisions

### Decision: Rich-based CLI over GUI

| Option | Tradeoff | Decision |
|--------|----------|----------|
| **Rich CLI** | Fast dev, cross-platform, meets all requirements, no browser | ✅ Adopted |
| TUI (Textual) | Overkill for 6 read/execute actions | ❌ Rejected |
| GUI (tkinter/PyQt) | Heavier, adds UI maintenance, out of scope per proposal | ❌ Rejected |

### Decision: Feature-based modules over layered architecture

| Option | Tradeoff | Decision |
|--------|----------|----------|
| **Feature modules** | Full independence, parallel implementation, easy testing | ✅ Adopted |
| Layered (controller/service/repo) | Over-engineered for scripts, adds coupling where none needed | ❌ Rejected |

### Decision: psutil for all OS metrics

| Option | Tradeoff | Decision |
|--------|----------|----------|
| **psutil** | Standard, battle-tested, cross-platform, single import for all metrics | ✅ Adopted |
| /proc filesystem parsing | Linux-only, brittle, more code | ❌ Rejected |
| platform + subprocess hacks | Inconsistent API surface, error-prone | ❌ Rejected |

### Decision: schedule + threading for automation

| Option | Tradeoff | Decision |
|--------|----------|----------|
| **schedule + threading** | Non-blocking, pure Python, simple API, enough for this scope | ✅ Adopted |
| cron / systemd timers | External dependency, not portable, user must configure | ❌ Rejected |
| asyncio | Adds complexity for no async-I/O benefit here | ❌ Rejected |

## Data Flow

```
User ──→ main.py (Rich Menu)
            │
            ├─ 1 → src/system_info.py ──→ psutil/platform ──→ Rich Layout → display
            ├─ 2 → src/process_monitor.py → psutil ──→ Rich Table → display
            ├─ 3 → src/file_organizer.py → pathlib/shutil → category dirs
            ├─ 4 → src/backup.py → shutil.copytree → timestamped log
            ├─ 5 → src/report_generator.py → gather data → TXT/CSV file
            └─ 6 → src/scheduler.py → schedule + thread → background loop
                   │
                   └── utils/helpers.py (console, fmt_bytes, error_handler)
```

All modules use `utils.helpers.console` (a shared `rich.console.Console` instance) for consistent output. The scheduler runs on a daemon thread so the main menu stays responsive.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `main.py` | Create | Entry point — Rich menu with options 1–6 and exit |
| `src/__init__.py` | Create | Package init (empty) |
| `src/system_info.py` | Create | OS/hardware/resource via psutil + platform, output in Rich panels |
| `src/process_monitor.py` | Create | List/search/kill processes, system-PID protection |
| `src/file_organizer.py` | Create | Categorize by extension into Documents/Images/Videos/Others |
| `src/backup.py` | Create | Recursive copy with Rich Progress bar + timestamped log |
| `src/report_generator.py` | Create | Gather all system data → write TXT or CSV report |
| `src/scheduler.py` | Create | Schedule/list/cancel backup/report/organize tasks |
| `utils/__init__.py` | Create | Package init (empty) |
| `utils/helpers.py` | Create | `console` instance, `fmt_bytes()`, `error_handler` decorator |
| `requirements.txt` | Create | psutil, rich, schedule |

## Testing Strategy

No test runner per `config.yaml` (strict_tdd: false). Acceptance verified manually:

| Module | Manual Check |
|--------|-------------|
| system_info | Run → verify OS, CPU, RAM, disk display |
| process_monitor | List processes → search by name → attempt kill of PID 1 (rejected) |
| file_organizer | Create mixed files → run → verify category folders |
| backup | Run on test dir → verify destination + log file |
| report_generator | Export TXT and CSV → verify content |
| scheduler | Schedule task → list it → wait for execution → cancel |

## Open Questions

- [ ] GitHub username for repo initialization and remote configuration?
