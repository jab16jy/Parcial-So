# System Information Specification

## Purpose

Display operating system, hardware, and resource usage details in a formatted Rich output.

## Requirements

### Requirement: Display OS Details

The system MUST show OS name, kernel version, and architecture when the user selects system info.

#### Scenario: Full OS info displayed

- GIVEN the user selects "System Information" from the menu
- WHEN the system queries OS details via `platform` and `psutil`
- THEN the system displays OS name, kernel version, and architecture in a Rich panel
- AND all fields are populated with non-empty values

#### Scenario: Unsupported OS metric

- GIVEN a platform-specific metric is unavailable (e.g., distribution name on Windows)
- WHEN the system attempts to retrieve that metric
- THEN the system SHOULD display "N/A" instead of failing

### Requirement: Display Hardware Details

The system MUST show CPU core count, total RAM, and disk capacity when requested.

#### Scenario: All hardware metrics available

- GIVEN the system has read permissions for hardware metrics
- WHEN the user requests hardware details
- THEN the system displays CPU physical/logical cores, total RAM in GB, and total disk space

#### Scenario: Permission denied on hardware metric

- GIVEN the user lacks read permission for a hardware metric (e.g., disk usage on restricted mount)
- WHEN the system attempts to read that metric
- THEN the system MUST display an inline warning and skip the unavailable metric
- AND MUST continue showing available metrics without aborting

### Requirement: Display Resource Usage

The system MUST show real-time CPU percentage, memory usage, and disk usage.

#### Scenario: Live resource snapshot

- GIVEN the system is running with normal permissions
- WHEN the user requests resource usage
- THEN the system shows current CPU %, used/total RAM, and used/total disk as a Rich table
- AND all values are read at call time (not cached)

#### Scenario: Metric reading failure

- GIVEN a resource metric raises an exception during read
- WHEN the system encounters the error
- THEN the system MUST catch the exception and display "Unavailable" for that row
- AND MUST continue rendering remaining metrics
