# File Organizer Specification

## Purpose

Auto-categorize files in a user-specified directory by file type into Documents, Images, Videos, and Others folders.

## Requirements

### Requirement: Categorize Files by Type

The system MUST classify files into Documents (.pdf, .doc, .txt, .md), Images (.jpg, .png, .gif, .bmp), Videos (.mp4, .avi, .mkv, .mov), and Others (everything else).

#### Scenario: Mixed file types organized correctly

- GIVEN a source directory containing .pdf, .jpg, .mp4, and .zip files
- WHEN the user runs the organizer
- THEN the system moves .pdf to Documents/, .jpg to Images/, .mp4 to Videos/, and .zip to Others/
- AND each target folder is created if it does not already exist

#### Scenario: File with unrecognized extension

- GIVEN a source directory contains a file whose extension is not in any category (e.g., .xyz)
- WHEN the system categorizes files
- THEN the file MUST be placed in the Others/ folder

### Requirement: Handle Duplicate Filenames

The system MUST NOT overwrite existing files in category folders when a duplicate name exists.

#### Scenario: Duplicate filename detected

- GIVEN the category folder already contains a file named "report.pdf"
- WHEN the organizer attempts to move another "report.pdf" into that folder
- THEN the system MUST append a timestamp or numeric suffix to the filename (e.g., "report_20260613_143022.pdf")
- AND MUST log the rename in the operation summary

#### Scenario: Filename collision with suffix variant

- GIVEN the category folder already contains "report.pdf" and "report_20260613_143022.pdf"
- WHEN the organizer attempts to move another "report.pdf"
- THEN the system MUST generate a new unique suffix different from existing variants

### Requirement: Handle Edge Case Directories

The system MUST handle empty, non-existent, or read-only directories gracefully.

#### Scenario: Empty source directory

- GIVEN the source directory exists but contains no files
- WHEN the user runs the organizer
- THEN the system MUST display "No files to organize" and exit cleanly

#### Scenario: Source directory does not exist

- GIVEN the source directory path does not exist on disk
- WHEN the user runs the organizer
- THEN the system MUST display an error message "Source directory not found: {path}"
- AND MUST NOT create any folders

#### Scenario: File move permission denied

- GIVEN a file in the source directory is not readable or movable due to permissions
- WHEN the organizer attempts to move it
- THEN the system MUST skip the file, log a warning, and continue with remaining files
