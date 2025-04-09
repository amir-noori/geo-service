from typing import Dict, List, Optional, Any
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime

from .base_task import BaseTask

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Manages scheduling and execution of tasks."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            jobstores={"default": MemoryJobStore()},
            timezone="UTC"
        )
        self.tasks: Dict[str, BaseTask] = {}
        self.logger = logger
    
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.info("Task scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info("Task scheduler shut down")
    
    def add_task(self, task: BaseTask):
        """
        Add a task to the scheduler.
        
        Args:
            task: The task to add
        """
        self.tasks[task.name] = task
        self.logger.info(f"Added task: {task.name}")
    
    def remove_task(self, task_name: str):
        """
        Remove a task from the scheduler.
        
        Args:
            task_name: Name of the task to remove
        """
        if task_name in self.tasks:
            del self.tasks[task_name]
            self.logger.info(f"Removed task: {task_name}")
    
    def schedule_task(
        self,
        task_name: str,
        trigger_type: str = "interval",
        **trigger_args
    ) -> bool:
        """
        Schedule a task for execution.
        
        Args:
            task_name: Name of the task to schedule
            trigger_type: Type of trigger ('interval', 'cron', or 'date')
            **trigger_args: Arguments for the trigger
            
        Returns:
            bool: True if scheduling was successful, False otherwise
        """
        if task_name not in self.tasks:
            self.logger.error(f"Task {task_name} not found")
            return False
        
        task = self.tasks[task_name]
        
        try:
            if trigger_type == "interval":
                trigger = IntervalTrigger(**trigger_args)
            elif trigger_type == "cron":
                trigger = CronTrigger(**trigger_args)
            elif trigger_type == "date":
                trigger = DateTrigger(**trigger_args)
            else:
                raise ValueError(f"Unknown trigger type: {trigger_type}")
            
            self.scheduler.add_job(
                task.execute,
                trigger=trigger,
                id=task_name,
                replace_existing=True
            )
            self.logger.info(f"Scheduled task {task_name} with {trigger_type} trigger")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to schedule task {task_name}: {str(e)}")
            return False
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        Get information about all scheduled tasks.
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing task information
        """
        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
                "task_info": self.tasks[job.id].get_task_info() if job.id in self.tasks else {}
            }
            for job in jobs
        ]
    
    def pause_task(self, task_name: str):
        """
        Pause a scheduled task.
        
        Args:
            task_name: Name of the task to pause
        """
        self.scheduler.pause_job(task_name)
        self.logger.info(f"Paused task: {task_name}")
    
    def resume_task(self, task_name: str):
        """
        Resume a paused task.
        
        Args:
            task_name: Name of the task to resume
        """
        self.scheduler.resume_job(task_name)
        self.logger.info(f"Resumed task: {task_name}") 