from datetime import datetime
from .base_task import BaseTask

class DatabaseCleanupTask(BaseTask):
    """Example task that cleans up old database records."""
    
    def __init__(self, days_to_keep: int = 30):
        super().__init__(
            name="database_cleanup",
            description="Cleans up old database records"
        )
        self.days_to_keep = days_to_keep
    
    async def execute(self, **kwargs):
        """
        Execute the database cleanup task.
        
        Args:
            **kwargs: Additional arguments that might be needed for task execution
        """
        self.logger.info(f"Starting database cleanup for records older than {self.days_to_keep} days")
        # Add your database cleanup logic here
        self.logger.info("Database cleanup completed")

class DataSyncTask(BaseTask):
    """Example task that syncs data between systems."""
    
    def __init__(self, source_system: str, target_system: str):
        super().__init__(
            name="data_sync",
            description=f"Syncs data from {source_system} to {target_system}"
        )
        self.source_system = source_system
        self.target_system = target_system
    
    async def execute(self, **kwargs):
        """
        Execute the data sync task.
        
        Args:
            **kwargs: Additional arguments that might be needed for task execution
        """
        self.logger.info(f"Starting data sync from {self.source_system} to {self.target_system}")
        # Add your data sync logic here
        self.logger.info("Data sync completed") 