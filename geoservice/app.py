import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from common.ApplicationContext import ApplicationContext
from geoservice.api.APIHandler import APIHandler
from geoservice.data.db_helper import get_db_connection_pool
from geoservice.tasks.health_check import HealthCheckTask
from tasks.scheduler import TaskScheduler
from geoservice.process.process_init import init_camunda_task_processing

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
    TODO: authentication
"""


async def startup_event_handler():
    scheduler.start()
    scheduler.schedule_task(
        "health_check",
        trigger_type="interval",
        minutes=1
    )
    await init_camunda_task_processing()
    logger.info("Task scheduler started and health check task scheduled")


async def shutdown_event_handler():
    scheduler.shutdown()
    logger.info("Task scheduler shut down")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: executed before the app starts
    print("Starting up...")
    await startup_event_handler()
    yield
    # Shutdown logic: executed after the app finishes
    print("Shutting down...")
    await shutdown_event_handler()


app_mode = os.environ["app_mode"]
enable_api_mock = os.environ["enable_api_mock"]

# Initialize task scheduler
scheduler = TaskScheduler()

# Create and add health check task
health_check_task = HealthCheckTask(app_mode=app_mode, enable_api_mock=enable_api_mock)
scheduler.add_task(health_check_task)

app = FastAPI(lifespan=lifespan)

ApplicationContext.app = app
APIHandler(app)

if app_mode == "app":
    ApplicationContext.connection_pool = get_db_connection_pool()

if app_mode == "dispatcher":
    if enable_api_mock == "false":
        from geoservice.api.parcels_api import load_states_polygons_list

        load_states_polygons_list()
