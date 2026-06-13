# Backup System Specification

## Purpose

Copy files from a user-specified source directory to a destination directory with a timestamped log entry for each operation.

## Requirements

### Requirement: Copy Files to Destination

The system MUST recursively copy all files from source to destination while preserving the directory structure.

#### Scenario: Successful backup of populated directory

- GIVEN a source directory with files and subdirectories
- WHEN the user initiates a backup
- THEN the system copies every file to the destination, preserving relative paths
- AND shows a Rich Progress bar during the copy operation

#### Scenario: Source directory does not exist

- GIVEN the specified source path does not exist
- WHEN the user initiates a backup
- THEN the system MUST display "Source directory not found: {path}"
- AND MUST NOT create a destination folder or perform any copy

### Requirement: Create Destination Folder

The system MUST create the destination directory if it does not already exist.

#### Scenario: Destination does not exist

- GIVEN the destination directory path does not exist
- WHEN the backup starts
- THEN the system creates the destination directory (and any parent directories)
- AND copies files into it

#### Scenario: Destination creation fails

- GIVEN the destination path is not writable (e.g., read-only filesystem)
- WHEN the system attempts to create the destination
- THEN the system MUST display "Cannot create destination: {path} — Permission denied"
- AND MUST abort the backup operation

### Requirement: Write Timestamped Log

The system MUST write a log file to the destination after each backup containing date/time, source path, destination path, and file count.

#### Scenario: Log written after successful backup

- GIVEN a backup operation completes successfully
- WHEN the copy finishes
- THEN the system creates a log file named "backup_YYYYMMDD_HHMMSS.log" in the destination
- AND the log contains the start timestamp, source, destination, and total file count

#### Scenario: Empty source directory

- GIVEN the source directory exists but contains no files (empty directory)
- WHEN the backup runs
- THEN the system creates the destination folder
- AND writes a log with file count 0
- AND displays notification that 0 files were copied

### Requirement: Handle Existing Destination

The system SHOULD merge files into an existing destination, overwriting files with the same name.

#### Scenario: Destination already exists with files

- GIVEN the destination exists and contains older files
- WHEN the backup runs
- THEN the system copies newer versions of files, overwriting existing ones
- AND the log reflects all files copied in this run
