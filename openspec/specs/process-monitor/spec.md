# Process Monitor Specification

## Purpose

List, search, and terminate processes with protection against killing critical system processes.

## Requirements

### Requirement: List All Processes

The system MUST display all running processes with PID, name, CPU %, and memory %.

#### Scenario: Normal process listing

- GIVEN the user selects "List Processes" from the menu
- WHEN the system reads the process table via `psutil`
- THEN the system displays a Rich table with PID, name, CPU %, and memory % for every running process
- AND rows are sorted by PID ascending

#### Scenario: No running processes (theoretical)

- GIVEN there are zero running processes (system boundary condition)
- WHEN the system reads the process table
- THEN the system MUST display a message "No processes found"
- AND NOT crash or produce an empty table

### Requirement: Search Processes by Name

The system MUST filter the process list by a user-provided name substring.

#### Scenario: Matching processes found

- GIVEN the user enters a search term (e.g., "python")
- WHEN the system filters processes by name containing that term
- THEN the system displays only matching processes in a Rich table

#### Scenario: No matches for search term

- GIVEN the user enters a search term that matches zero processes
- WHEN the system filters and finds no matches
- THEN the system MUST display "No processes matching '{term}' found"

### Requirement: Kill Process by PID

The system MUST terminate a process by PID after user confirmation.

#### Scenario: Kill non-system process successfully

- GIVEN a non-protected PID provided by the user
- WHEN the user confirms the kill action
- THEN the system terminates the process and displays a success message

#### Scenario: Kill non-existent PID

- GIVEN a PID that does not correspond to any running process
- WHEN the user attempts to kill it
- THEN the system MUST display "No process with PID {pid} found"
- AND MUST NOT raise an unhandled exception

### Requirement: System-Process Protection

The system MUST prevent killing processes with PID 1 or other protected system PIDs.

#### Scenario: Attempt to kill PID 1

- GIVEN the user enters PID 1 (init/systemd)
- WHEN the kill request is submitted
- THEN the system MUST reject the request with message "Cannot terminate PID 1: system-protected process"
- AND MUST NOT send a kill signal

#### Scenario: Attempt to kill protected system process

- GIVEN the user enters a PID owned by root and identified as a system service
- WHEN the kill request is submitted
- THEN the system MUST warn the user and require additional confirmation
- AND MAY still reject the kill if the process is on the protected list
