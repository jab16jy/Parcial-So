# Report Generator Specification

## Purpose

Export system information, resource usage statistics, and active process lists to TXT or CSV format files.

## Requirements

### Requirement: Export TXT Report

The system MUST generate a plain-text report file containing OS info, hardware details, CPU/memory/disk usage, and active process table.

#### Scenario: TXT report created with full data

- GIVEN the user selects "Export as TXT"
- WHEN the system gathers OS, hardware, resource, and process data
- THEN the system writes a formatted TXT file with clear section headers for each data category
- AND saves it as "report_YYYYMMDD_HHMMSS.txt" in the current directory

#### Scenario: Some data unavailable in TXT

- GIVEN one or more data sources fail (e.g., permission denied on disk usage)
- WHEN the system generates the report
- THEN the system writes "Unavailable" or "Error retrieving data" for the affected sections
- AND the report still contains all other available sections

### Requirement: Export CSV Report

The system MUST generate a CSV report with the same data scope as the TXT report.

#### Scenario: CSV report created with structured data

- GIVEN the user selects "Export as CSV"
- WHEN the system gathers all data
- THEN the system writes a CSV file with a header row and data rows organized by category
- AND saves it as "report_YYYYMMDD_HHMMSS.csv"

#### Scenario: CSV with empty process list

- GIVEN there are no running processes (system boundary condition)
- WHEN the system generates the CSV
- THEN the process section of the CSV MUST contain only the header row with a note "No processes"
- AND other sections MUST be fully populated

### Requirement: Handle File Write Failures

The system MUST handle cases where the report file cannot be written.

#### Scenario: Write permission denied

- GIVEN the current directory does not have write permissions
- WHEN the system attempts to write the report
- THEN the system MUST display "Cannot write report: Permission denied — {path}"
- AND MUST NOT create a partial or empty file

#### Scenario: Disk full

- GIVEN the disk has insufficient space for the report file
- WHEN the system attempts to write
- THEN the system MUST catch the IOError and display a user-friendly error message
