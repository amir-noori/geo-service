import asyncio
import logging
from typing import Dict, Any, List, Callable, Optional

import pycamunda.externaltask
from pycamunda.externaltask import ExternalTask

logger = logging.getLogger(__name__)


class CamundaTaskHandler:
    """
    Handler for Camunda 7 external tasks that integrates with FastAPI.
    This class fetches tasks from Camunda, processes them, and completes or fails them.
    """

    def __init__(self,
                 camunda_url: str,
                 worker_id: str,
                 topics: List[Dict[str, Any]],
                 max_tasks: int = 10):
        """
        Initialize the Camunda task handler.

        Args:
            camunda_url: URL of the Camunda engine
            worker_id: ID of the worker that will process the tasks
            topics: List of topics to fetch tasks from
            max_tasks: Maximum number of tasks to fetch at once
        """
        self.camunda_url = camunda_url
        self.worker_id = worker_id
        self.topics = topics
        self.max_tasks = max_tasks
        self.task_handlers: Dict[str, Callable] = {}
        self.is_running = False
        self.task_loop = None
        self.logger = logger.getChild("camunda_handler")
        self.fetch_and_lock = pycamunda.externaltask.FetchAndLock(url=self.camunda_url, worker_id=self.worker_id,
                                                                  max_tasks=self.max_tasks)
        for topic in self.topics:
            self.fetch_and_lock.add_topic(name=topic['topicName'], lock_duration=topic['lockDuration'])

    def register_task_handler(self, topic_name: str, handler_func: Callable):
        """
        Register a handler function for a specific topic.

        Args:
            topic_name: Name of the topic to handle
            handler_func: Function to handle tasks from this topic
        """
        self.task_handlers[topic_name] = handler_func
        self.logger.debug(f"Registered handler for topic: {topic_name}")

    async def start(self):
        """Start the task handler."""
        if self.is_running:
            self.logger.warning("Task handler is already running")
            return

        self.is_running = True
        self.task_loop = asyncio.create_task(self._task_loop())
        self.logger.debug("Camunda task handler started")

    async def stop(self):
        """Stop the task handler."""
        if not self.is_running:
            self.logger.warning("Task handler is not running")
            return

        self.is_running = False
        if self.task_loop:
            self.task_loop.cancel()
            try:
                await self.task_loop
            except asyncio.CancelledError:
                pass
            self.task_loop = None
        self.logger.debug("Camunda task handler stopped")

    async def _task_loop(self):
        """Main task processing loop."""
        while self.is_running:
            try:
                # Fetch tasks from Camunda
                tasks = self.fetch_and_lock()
                if not tasks:
                    self.logger.debug("No tasks found to process")
                    await asyncio.sleep(1)  # Short delay when no tasks
                    continue

                self.logger.debug(f"Found {len(tasks)} tasks to process")

                # Process each task
                for task in tasks:
                    await self._process_task(task)

            except Exception as e:
                self.logger.error(f"Error in task processing loop: {str(e)}")
                await asyncio.sleep(5)  # Wait longer on error

    async def _process_task(self, task: ExternalTask):
        """
        Process a single task from Camunda.

        Args:
            task: The task to process
        """
        task_id = task.id_
        topic_name = task.topic_name

        self.logger.debug(f"Processing task {task_id} from topic {topic_name}")

        try:
            # Check if we have a handler for this topic
            if topic_name not in self.task_handlers:
                self.logger.warning(f"No handler registered for topic {topic_name}")
                await self._handle_failure(task, f"No handler registered for topic {topic_name}")
                return

            # Get the handler for this topic
            handler = self.task_handlers[topic_name]

            # Process the task
            result = await handler(task)

            # Complete the task
            await self._complete_task(task, result)

        except Exception as e:
            self.logger.error(f"Error processing task {task_id}: {str(e)}")
            await self._handle_failure(task, str(e))

    async def _complete_task(self, task: ExternalTask, variables: Optional[Dict[str, Any]] = None):
        """
        Complete a task in Camunda.

        Args:
            task: The task to complete
            variables: Variables to set when completing the task
        """
        try:
            complete = pycamunda.externaltask.Complete(url=self.camunda_url, id_=task.id_,
                                                       worker_id=self.worker_id)
            # @TODO : complete.add_variable(name='ServiceTaskVariable', value=2)
            complete()
            self.logger.debug(f"Completed task {task.id_}")
        except Exception as e:
            self.logger.error(f"Error completing task {task.id_}: {str(e)}")
            raise

    async def _handle_failure(self, task: ExternalTask, error_message: str, retries: int = 0, retry_timeout: int = 0):
        """
        Handle a task failure in Camunda.

        Args:
            task: The task that failed
            error_message: Message describing the error
            retries: Number of retries left
            retry_timeout: Timeout in milliseconds before retrying
        """
        try:
            failure = pycamunda.externaltask.HandleFailure(url=self.camunda_url, id_=task.id_, worker_id=self.worker_id,
                                                           error_message=error_message,
                                                           retries=retries,
                                                           error_details="TODO", # TODO
                                                           retry_timeout=retry_timeout)
            # TODO: add variable?
            failure()
            self.logger.debug(f"Reported failure for task {task.id_}: {error_message}")
        except Exception as e:
            self.logger.error(f"Error reporting failure for task {task.id_}: {str(e)}")
            raise
