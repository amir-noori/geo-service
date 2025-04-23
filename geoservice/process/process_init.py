import os
from process.CamundaTaskHandler import CamundaTaskHandler
from geoservice.process.sample_task import handle_test_task
from geoservice.process.claim_process_tasks import handle_persist_claim_request_task, handle_send_request_to_tom_task, \
    handle_inform_kateb_about_surveyor_task, handle_notify_kateb_about_survey_status_task
import logging

logger = logging.getLogger(__name__)

async def init_camunda_task_processing():
    # Camunda configuration
    camunda_url = os.environ.get("CAMUNDA_URL", "http://localhost:7171/engine-rest")
    camunda_worker_id = os.environ.get("CAMUNDA_WORKER_ID", "geoservice-worker")
    camunda_topics = [
        {"topicName": "test-external-task", "lockDuration": 10000},
        {"topicName": "persist-claim-request", "lockDuration": 10000},
        {"topicName": "send-request-to-tom", "lockDuration": 10000},
        {"topicName": "inform-kateb-about-surveyor", "lockDuration": 10000},
        {"topicName": "notify-kateb-about-claim-survey", "lockDuration": 10000},
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
    camunda_handler.register_task_handler("persist-claim-request", handle_persist_claim_request_task)
    camunda_handler.register_task_handler("send-request-to-tom", handle_send_request_to_tom_task)
    camunda_handler.register_task_handler("inform-kateb-about-surveyor", handle_inform_kateb_about_surveyor_task)
    camunda_handler.register_task_handler("notify-kateb-about-claim-survey", handle_notify_kateb_about_survey_status_task)

    logger.debug("starting camunda task handler...")
    await camunda_handler.start()
    logger.debug("camunda task handler started.")
