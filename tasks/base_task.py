from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BaseTask(ABC):
    """Base class for all scheduled tasks."""
    
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description or f"Task {name}"
        self.logger = logger.getChild(name)
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the task. This method must be implemented by all task classes.
        
        Args:
            **kwargs: Additional arguments that might be needed for task execution
            
        Returns:
            Any: The result of the task execution
        """
        pass
    
    def get_task_info(self) -> Dict[str, str]:
        """
        Get information about the task.
        
        Returns:
            Dict[str, str]: Dictionary containing task information
        """
        return {
            "name": self.name,
            "description": self.description,
            "class": self.__class__.__name__
        }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"