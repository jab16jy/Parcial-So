# Scheduled Automation Specification

## Purpose

Schedule, list, and cancel automated backup, report generation, and file organization tasks using the `schedule` library.

## Requirements

### Requirement: Schedule a Task

The system MUST allow the user to schedule backup, report, or organization tasks at a specified interval (minutes, hours, or daily).

#### Scenario: Schedule a recurring backup

- GIVEN the user selects "Schedule Backup" and provides an interval (e.g., "every 30 minutes")
- WHEN the system validates and registers the task
- THEN the task is added to the scheduler with the specified interval
- AND the system confirms with "Backup scheduled every 30 minutes"

#### Scenario: Invalid interval format

- GIVEN the user provides a non-parsable interval (e.g., "every banana")
- WHEN the system attempts to parse the interval
- THEN the system MUST display "Invalid interval: {input}. Use format: every N minutes/hours"
- AND MUST NOT add the task to the scheduler

### Requirement: List Scheduled Tasks

The system MUST display all currently scheduled tasks with their type and next run time.

#### Scenario: Tasks are scheduled

- GIVEN one or more tasks have been added to the scheduler
- WHEN the user selects "List Scheduled Tasks"
- THEN the system displays a Rich table with task type, interval, and next run time for each task

#### Scenario: No tasks scheduled

- GIVEN no tasks have been added to the scheduler
- WHEN the user selects "List Scheduled Tasks"
- THEN the system MUST display "No tasks currently scheduled"

### Requirement: Cancel a Scheduled Task

The system MUST allow the user to remove a specific scheduled task by selecting it from the task list.

#### Scenario: Cancel existing task

- GIVEN a task is currently scheduled
- WHEN the user selects it for cancellation
- THEN the system removes the task from the scheduler
- AND displays "{task} has been cancelled"

#### Scenario: Cancel non-existent task

- GIVEN the task list is empty
- WHEN the user attempts to cancel a task
- THEN the system MUST display "No tasks to cancel"

### Requirement: Execute Scheduled Tasks

The system MUST run scheduled tasks at their configured intervals while the scheduler is active.

#### Scenario: Backup runs at scheduled time

- GIVEN a backup task is scheduled every hour
- WHEN the scheduled time arrives
- THEN the system executes the backup function with the last-used source and destination paths
- AND logs the execution to the backup log

#### Scenario: Task execution fails

- GIVEN a scheduled task encounters an error during execution (e.g., source directory missing)
- WHEN the task runs
- THEN the system MUST catch the exception and log the failure
- AND the task MUST remain scheduled for future runs (not be removed on failure)
