import os
from process.CamundaTaskHandler import CamundaTaskHandler
from geoservice.process.test_tasks import handle_test_task


async def init_camunda_task_processing():
    # Camunda configuration
    camunda_url = os.environ.get("CAMUNDA_URL", "http://localhost:7171/engine-rest")
    camunda_worker_id = os.environ.get("CAMUNDA_WORKER_ID", "geoservice-worker")
    camunda_topics = [
        {"topicName": "test-external-task", "lockDuration": 10000}
    ]

    # Initialize Camunda task handler
    camunda_handler = CamundaTaskHandler(
        camunda_url=camunda_url,
        worker_id=camunda_worker_id,
        topics=camunda_topics,
        max_tasks=10
    )

    # Register task handlers
    camunda_handler.register_task_handler("test-external-task", handle_test_task)

    await camunda_handler.start()