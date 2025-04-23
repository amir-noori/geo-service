import json
import logging
import os
from typing import Dict, Any, List

import requests
from shapely import wkt

from geoservice.common.constants import GLOBAL_SRID
from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ServiceException
from geoservice.model.entity.Claim import ParcelClaim, RegisteredClaim
from geoservice.model.entity.Person import Person
from geoservice.service.claim_service import save_new_claim_parcel_request, query_parcel_claim_request, \
    update_parcel_claim_request, query_registered_parcel_claim_request
from geoservice.service.person_service import query_person, create_person

logger = logging.getLogger(__name__)


async def query_surveyor(parcel_claim: ParcelClaim):
    surveyor_id = parcel_claim.surveyor_id
    surveyors: List[Person] = query_person(Person(id=surveyor_id))
    surveyor: Person = None
    if len(surveyors) > 0:
        surveyor = surveyors[0]

    return surveyor

async def query_claim(request_id) -> ParcelClaim:
    parcel_claim_list = List[ParcelClaim] = query_parcel_claim_request(request_id)
    parcel_claim: ParcelClaim = parcel_claim_list[0] if len(parcel_claim_list) > 0 else None
    if not parcel_claim:
        raise ServiceException(ErrorCodes.PROCESS_CLAIM_DATA_NOT_FOUND,
                               error_message=f"cannot find claim by request id {request_id}")

    return parcel_claim


async def handle_persist_claim_request_task(task) -> Dict[str, Any]:
    logger.info(f"Processing persist claim request task {task.id_}")

    try:
        variables = task.variables
        logger.debug(f"Processing test task {variables}")
        request_claim_data = variables.get("requestClaimData", {})
        request_id = request_claim_data.get("requestId")
        claimant = request_claim_data.get("claimant")
        surveyor = request_claim_data.get("surveyor")
        cms = request_claim_data.get("cms")
        neighbouring_point_wkt = request_claim_data.get("neighbouring_point_wkt")

        if not request_id and not claimant:
            error_message = f"claim data not found: request_id: {request_id}, claimant: {claimant}"
            raise ServiceException(ErrorCodes.PROCESS_CLAIM_DATA_NOT_FOUND, error_message=error_message)

        save_new_claim_parcel_request(request_id, claimant, surveyor, cms,
                                      neighbouring_point_wkt, task.process_instance_id)

        return {
            "status": "SUCCESS",
            "message": "claim request registered successfully"
        }

    except Exception as e:
        # TODO : check if returned status is ERROR the activity can be retried again
        logger.error(f"Error test registration task: {str(e)}")
        return {
            "status": "ERROR",
            "errorMessage": str(e)
        }


async def handle_send_request_to_tom_task(task) -> Dict[str, Any]:
    logger.info(f"Processing send request to tom task {task.id_}")

    try:
        variables = task.variables
        logger.debug(f"Processing test task {variables}")
        request_claim_data = variables.get("requestClaimData", {})
        request_id = request_claim_data.get("requestId")
        parcel_claim: ParcelClaim = await query_claim(request_id)
        neighbouring_point_wkt = parcel_claim.neighbouring_point
        neighbouring_point = wkt.loads(neighbouring_point_wkt)
        claimant_id = parcel_claim.claimant_id
        claimant: Person = query_person(Person(id=claimant_id))[0]
        surveyor: Person = await query_surveyor(parcel_claim)

        tom_service_base_url = os.environ.get("TOM_SERVICE_URL", "http://localhost:5002")
        tom_assign_surveyor_service_path = os.environ.get("TOM_ASSIGN_SURVEYOR_SERVICE_PATH", "assignSurveyor")
        url = f"{tom_service_base_url}/{tom_assign_surveyor_service_path}"

        response = requests.post(url, json={
            "requestId": request_id,
            "claimant": claimant,
            "surveyor": surveyor,
            "neighborhoodPoint": {
                "x": neighbouring_point.x,
                "y": neighbouring_point.y,
                "SRS": str(GLOBAL_SRID)
            }
        })
        if response.status_code == 200:
            response_content = json.loads(response.content.decode('utf-8'))
            logger.debug(response_content)

            assigned_surveyor_data = response_content["surveyor"]
            assigned_surveyor = Person(first_name=assigned_surveyor_data["first_name"],
                                       last_name=assigned_surveyor_data["last_name"],
                                       national_id=assigned_surveyor_data["national_id"],
                                       phone_number=assigned_surveyor_data["phone_number"],
                                       birthday=assigned_surveyor_data["birthday"])
            assigned_surveyor = create_person(assigned_surveyor)
            parcel_claim.surveyor = assigned_surveyor.id
            update_parcel_claim_request(parcel_claim)

        else:
            logger.error(f"error code: {response.status_code}")
            logger.error(f"error {response.content}")
            return {
                "status": "ERROR",
                "errorMessage": f"error in calling TOM service: response code: {{response.status_code}}, response content {response.content}"
            }

        return {
            "status": "SUCCESS",
            "message": "survey request sent to TOM successfully"
        }

    except Exception as e:
        logger.error(f"Error sending survey request to TOM: {str(e)}")
        return {
            "status": "ERROR",
            "errorMessage": str(e)
        }


async def handle_inform_kateb_about_surveyor_task(task) -> Dict[str, Any]:
    logger.info(f"Processing inform kateb about surveyor task {task.id_}")

    try:
        variables = task.variables
        logger.debug(f"Processing test task {variables}")
        request_claim_data = variables.get("requestClaimData", {})
        request_id = request_claim_data.get("requestId")
        parcel_claim: ParcelClaim = await query_claim(request_id)
        surveyor: Person = await query_surveyor(parcel_claim)

        url = os.environ.get("KATEB_NOTIFY_SURVEYOR_SERVICE_URL", "https://26dc4823-95ee-4f4c-8c90-e33fdcc32993.mock.pstmn.io/surveyorStatusUpdate")
        response = requests.post(url, json={
            "requestId": request_id,
            "surveyor": surveyor
        })
        if response.status_code == 200:
            response_content = json.loads(response.content.decode('utf-8'))
            logger.debug(response_content)
        else:
            return {
                "status": "ERROR",
                "errorMessage": f"error in calling Kateb service: response code: {{response.status_code}}, response content {response.content}"
            }

        return {
            "status": "SUCCESS",
            "message": "survey request sent to TOM successfully"
        }

    except Exception as e:
        logger.error(f"Error notifying Kateb about surveyor: {str(e)}")
        return {
            "status": "ERROR",
            "errorMessage": str(e)
        }


async def handle_notify_kateb_about_survey_status_task(task) -> Dict[str, Any]:
    logger.info(f"Processing inform kateb about survey status task {task.id_}")

    try:
        variables = task.variables
        logger.debug(f"Processing test task {variables}")
        request_claim_data = variables.get("requestClaimData", {})
        request_id = request_claim_data.get("requestId")
        registered_claim: RegisteredClaim = query_registered_parcel_claim_request(
            RegisteredClaim(request_id=request_id))

        url = os.environ.get("KATEB_NOTIFY_SURVEY_STATUS_SERVICE_URL", "https://26dc4823-95ee-4f4c-8c90-e33fdcc32993.mock.pstmn.io/surveyStatusUpdate")
        response = requests.post(url, json={
            "requestId": request_id,
            "claimTracingId": registered_claim.claim_tracing_id,
            "status": registered_claim.status
        })
        if response.status_code == 200:
            response_content = json.loads(response.content.decode('utf-8'))
            logger.debug(response_content)
        else:
            return {
                "status": "ERROR",
                "errorMessage": f"error in calling Kateb service: response code: {{response.status_code}}, response content {response.content}"
            }

        return {
            "status": "SUCCESS",
            "message": "survey request sent to TOM successfully"
        }

    except Exception as e:
        logger.error(f"Error sending survey request to TOM: {str(e)}")
        return {
            "status": "ERROR",
            "errorMessage": str(e)
        }
