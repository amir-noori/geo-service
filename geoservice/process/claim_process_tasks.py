import json
import logging
import os
from typing import Dict, Any, List

import requests
from fastapi.encoders import jsonable_encoder
from shapely import wkt

from geoservice.api.external.apigw import call_downstream_service_post
from geoservice.api.external.tom import call_tom_assign_surveyor
from geoservice.exception.common import ErrorCodes
from geoservice.exception.persist_exception import CustomerExistsException
from geoservice.exception.process_exception import ProcessException
from geoservice.exception.service_exception import ServiceException
from geoservice.model.dto.PersonDTO import PersonDTO
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
    parcel_claim_list: List[ParcelClaim] = query_parcel_claim_request(request_id)
    parcel_claim: ParcelClaim = parcel_claim_list[0] if len(parcel_claim_list) > 0 else None
    if not parcel_claim:
        raise ServiceException(ErrorCodes.PROCESS_CLAIM_DATA_NOT_FOUND,
                               error_message=f"cannot find claim by request id {request_id}")

    return parcel_claim


def get_process_variables(task):
    variables = task.variables
    logger.debug(f"Processing test task {variables}")

    claimant_dict = None
    surveyor_dict = None

    if variables.get("claimant"):
        claimant_dict = variables.get("claimant").value
    if variables.get("surveyor"):
        surveyor_dict = variables.get("surveyor").value

    claimant_dto: PersonDTO = None
    surveyor_dto: PersonDTO = None

    if claimant_dict:
        claimant_dto = PersonDTO.from_dict(claimant_dict)
    if surveyor_dict:
        surveyor_dto = PersonDTO.from_dict(surveyor_dict)

    return {
        "requestId": variables.get("requestId").value,
        "claimant": claimant_dto,
        "surveyor": surveyor_dto,
        "cms": variables.get("cms").value,
        "neighborhoodPoint": variables.get("neighborhoodPoint").value,
        "srs": variables.get("srs").value,
    }


async def handle_persist_claim_request_task(task) -> Dict[str, Any]:
    logger.info(f"Processing persist claim request task {task.id_}")

    try:
        variables = get_process_variables(task)
        request_id = variables["requestId"]
        claimant = variables["claimant"]
        surveyor = variables["surveyor"]
        cms = variables["cms"]
        neighbouring_point_wkt = variables["neighborhoodPoint"]
        srs = variables["srs"]

        if not request_id and not claimant:
            error_message = f"claim data not found: request_id: {request_id}, claimant: {claimant}"
            raise ServiceException(ErrorCodes.PROCESS_CLAIM_DATA_NOT_FOUND, error_message=error_message)

        save_new_claim_parcel_request(request_id, claimant, surveyor, cms,
                                      neighbouring_point_wkt, task.process_instance_id, srs)

        return {
            "status": "SUCCESS",
            "message": "claim request registered successfully"
        }

    except Exception as e:
        logger.error(f"Error test registration task: {str(e)}")
        raise e


async def handle_send_request_to_tom_task(task) -> Dict[str, Any]:
    logger.info(f"Processing send request to tom task {task.id_}")
    try:
        variables = get_process_variables(task)
        request_id = variables["requestId"]
        parcel_claim: ParcelClaim = await query_claim(request_id)
        neighbouring_point_wkt = parcel_claim.neighbouring_point
        neighbouring_point = wkt.loads(neighbouring_point_wkt)
        claimant_id = parcel_claim.claimant_id
        claimant: Person = query_person(Person(id=claimant_id))[0]
        surveyor: Person = await query_surveyor(parcel_claim)

        assigned_surveyor, claim_tracing_id, sms_message = call_tom_assign_surveyor(parcel_claim,
                                                                                    PersonDTO.from_dict(
                                                                                        jsonable_encoder(claimant)),
                                                                                    PersonDTO.from_dict(
                                                                                        jsonable_encoder(surveyor)))

        assigned_surveyor = Person(first_name=assigned_surveyor.first_name,
                                   last_name=assigned_surveyor.last_name,
                                   national_id=assigned_surveyor.national_id,
                                   phone_number=assigned_surveyor.phone_number,
                                   mobile_number=assigned_surveyor.mobile_number)
        try:
            assigned_surveyor = create_person(assigned_surveyor)
        except CustomerExistsException as e:
            assigned_surveyor = e.person
        parcel_claim.surveyor = assigned_surveyor.id
        update_parcel_claim_request(parcel_claim)

        return {
            "status": "SUCCESS",
            "message": "survey request sent to TOM successfully"
        }

    except Exception as e:
        logger.error(f"Error sending survey request to TOM: {str(e)}")
        raise e


async def handle_inform_kateb_about_surveyor_task(task) -> Dict[str, Any]:
    logger.info(f"Processing inform kateb about surveyor task {task.id_}")

    try:
        variables = get_process_variables(task)
        request_id = variables["requestId"]
        parcel_claim: ParcelClaim = await query_claim(request_id)
        surveyor: Person = await query_surveyor(parcel_claim)

        url = os.environ.get("KATEB_NOTIFY_SURVEYOR_SERVICE_URL",
                             "https://26dc4823-95ee-4f4c-8c90-e33fdcc32993.mock.pstmn.io/surveyorStatusUpdate")
        request = {
            "requestId": request_id,
            "surveyor": jsonable_encoder(PersonDTO.from_dict(jsonable_encoder(surveyor)))
        }
        response = call_downstream_service_post(service_url=url, payload=request)
        if response.status_code == 200:
            response_content = json.loads(response.content.decode('utf-8'))
            logger.debug(response_content)
        else:
            error_message = f"error in calling Kateb service: response code: {{response.status_code}}, response content {response.content}"
            logging.error(error_message)
            raise ProcessException(error_message)

        return {
            "status": "SUCCESS",
            "message": "inform kateb about surveyor successfully"
        }

    except Exception as e:
        logger.error(f"Error notifying Kateb about surveyor: {str(e)}")
        raise e


async def handle_update_claim_with_cadastre_data_task(task) -> Dict[str, Any]:
    logger.info(f"Processing update claim with cadastre data task {task.id_}")

    try:
        variables = get_process_variables(task)
        request_id = variables["requestId"]
        parcel_claim: ParcelClaim = await query_claim(request_id)

        # TODO: call cadastre
        # url = os.environ.get("???", "???")
        # response = requests.post(url, json={})
        # if response.status_code == 200:
        #     response_content = json.loads(response.content.decode('utf-8'))
        #     logger.debug(response_content)
        # else:
        #     error_message = f"error in calling cadastre service: response code: {{response.status_code}}, response content {response.content}"
        #     logger.error(error_message)
        #     ProcessException(error_message)

        return {
            "status": "SUCCESS",
            "message": "update claim with cadastre data successfully"
        }

    except Exception as e:
        logger.error(f"Error update claim with cadastre data: {str(e)}")
        raise e


async def handle_notify_kateb_about_survey_status_task(task) -> Dict[str, Any]:
    logger.info(f"Processing inform kateb about survey status task {task.id_}")

    try:
        variables = get_process_variables(task)
        request_id = variables["requestId"]
        registered_claim: RegisteredClaim = query_registered_parcel_claim_request(
            RegisteredClaim(request_id=request_id))

        url = os.environ.get("KATEB_NOTIFY_SURVEY_STATUS_SERVICE_URL",
                             "https://26dc4823-95ee-4f4c-8c90-e33fdcc32993.mock.pstmn.io/surveyStatusUpdate")
        request = {
            "requestId": request_id,
            "claimTracingId": registered_claim.claim_tracing_id,
            "status": registered_claim.status
        }
        response = call_downstream_service_post(service_url=url, payload=request)

        if response.status_code == 200:
            response_content = json.loads(response.content.decode('utf-8'))
            logger.debug(response_content)
        else:
            error_message = f"error in calling Kateb service: response code: {{response.status_code}}, response content {response.content}"
            logger.error(error_message)
            ProcessException(error_message)

        return {
            "status": "SUCCESS",
            "message": "inform kateb about survey status successfully"
        }

    except Exception as e:
        logger.error(f"Error sending survey request to TOM: {str(e)}")
        raise e
