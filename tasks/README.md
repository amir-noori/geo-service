# Task Scheduling System

This package provides a flexible task scheduling system for the QGIS server application. It uses APScheduler for managing scheduled tasks and provides a simple interface for creating and managing tasks.

## Features

- Async task execution
- Multiple trigger types (interval, cron, date)
- Task management (add, remove, pause, resume)
- Logging integration
- Easy task creation through inheritance

## Usage

### Creating a Task

Create a new task by inheriting from `BaseTask`:

```python
from tasks.base_task import BaseTask

class MyTask(BaseTask):
    def __init__(self):
        super().__init__(
            name="my_task",
            description="Description of my task"
        )
    
    async def execute(self, **kwargs):
        # Your task logic here
        pass
```

### Using the Scheduler

```python
from tasks.scheduler import TaskScheduler
from tasks.example_tasks import DatabaseCleanupTask

# Create scheduler
scheduler = TaskScheduler()

# Create and add tasks
cleanup_task = DatabaseCleanupTask(days_to_keep=30)
scheduler.add_task(cleanup_task)

# Start the scheduler
scheduler.start()

# Schedule tasks
# Run every hour
scheduler.schedule_task(
    "database_cleanup",
    trigger_type="interval",
    hours=1
)

# Run daily at midnight
scheduler.schedule_task(
    "database_cleanup",
    trigger_type="cron",
    hour=0,
    minute=0
)

# Run at a specific date
scheduler.schedule_task(
    "database_cleanup",
    trigger_type="date",
    run_date="2024-12-31 23:59:59"
)
```

### Task Management

```python
# Get all scheduled tasks
tasks = scheduler.get_scheduled_tasks()

# Pause a task
scheduler.pause_task("database_cleanup")

# Resume a task
scheduler.resume_task("database_cleanup")

# Remove a task
scheduler.remove_task("database_cleanup")

# Shutdown the scheduler
scheduler.shutdown()
```

## Trigger Types

### Interval Trigger
Run tasks at fixed intervals:
```python
scheduler.schedule_task(
    "task_name",
    trigger_type="interval",
    seconds=30,  # Run every 30 seconds
    minutes=5,   # Run every 5 minutes
    hours=1      # Run every hour
)
```

### Cron Trigger
Run tasks at specific times:
```python
scheduler.schedule_task(
    "task_name",
    trigger_type="cron",
    day_of_week="mon-fri",  # Monday to Friday
    hour=9,                 # At 9 AM
    minute=30              # At 30 minutes
)
```

### Date Trigger
Run tasks at a specific date and time:
```python
scheduler.schedule_task(
    "task_name",
    trigger_type="date",
    run_date="2024-12-31 23:59:59"
)
```

## Best Practices

1. Always implement proper error handling in your tasks
2. Use logging to track task execution
3. Keep task execution time reasonable
4. Use appropriate trigger types for your use case
5. Consider timezone settings when scheduling tasks 