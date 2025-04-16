import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


async def handle_test_task(task) -> Dict[str, Any]:
    logger.info(f"Processing test task {task.id_}")

    try:
        # Extract variables from the task
        variables = task.variables
        logger.info(f"Processing test task {variables}")
        return {
            "status": "SUCCESS",
            "message": "test task done successfully"
        }

    except Exception as e:
        logger.error(f"Error test registration task: {str(e)}")
        # Return error variables
        return {
            "status": "ERROR",
            "errorMessage": str(e)
        }