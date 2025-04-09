import logging
from datetime import datetime

from tasks.base_task import BaseTask

logger = logging.getLogger(__name__)

class HealthCheckTask(BaseTask):
    """Simple task that logs application health status."""
    
    def __init__(self, app_mode: str, enable_api_mock: str):
        super().__init__(
            name="health_check",
            description="Logs application health status every minute"
        )
        self.app_mode = app_mode
        self.enable_api_mock = enable_api_mock
    
    async def execute(self, **kwargs):
        """Execute the health check task."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"Health check at {current_time} - Application is running")
        self.logger.info(f"App mode: {self.app_mode}, API mock enabled: {self.enable_api_mock}") 