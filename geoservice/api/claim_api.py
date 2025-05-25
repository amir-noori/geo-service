import base64
import json
import os
from datetime import datetime
import random
from typing import List

import requests.auth
from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from pycamunda.message import CorrelateSingle
from pycamunda.processdef import StartInstance
from shapely.geometry import Polygon
from shapely.geometry import shape
from shapely.wkt import loads

from common.str_util import base64ToString, parse_to_int, parse_to_float
from geoservice.api.common import handle_response
from geoservice.api.route import route
from geoservice.api.utils import call_cadastre_api
from geoservice.common.constants import GLOBAL_SRID
from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ServiceException
from geoservice.model.dto.BaseDTO import Header
from geoservice.model.dto.BaseDTO import RequestHeader
from geoservice.model.dto.ParcelDtoRequest import PolygonWrapperCmsDTO, WrapperCmsRequest, GetOverlappingParcelsDTO, \
    GetOverlappingParcelsRequest
from geoservice.model.dto.ParcelDtoResponse import WrapperCmsResponse, OverlappingResponse, OverlappingResponseDTO
from geoservice.model.dto.PersonDTO import PersonDTO
from geoservice.model.dto.claim.ClaimDtoReq import ClaimRequest, ClaimParcelQueryRequest, RegisterNewClaimRequest, \
    RegisterNewClaimRequestDTO, RegisterNewClaimCallbackRequestDTO, RegisterNewClaimCallbackRequest, \
    ClaimParcelSurveyQueryRequest, ClaimParcelSurveyQueryRequestDTO, ParcelMetadataDTO
from geoservice.model.dto.claim.ClaimDtoReq import ClaimRequestDTO, ClaimParcelQueryRequestDTO
from geoservice.model.dto.claim.ClaimDtoResponse import ClaimResponse, ClaimParcelQueryResponse, \
    ClaimParcelQueryResponseDTO, ClaimResponseDTO, RegisterNewClaimResponseDTO, RegisterNewClaimResponse, \
    RegisterNewClaimCallbackResponse, RegisterNewClaimCallbackResponseDTO, ClaimParcelSurveyQueryResponse, \
    ClaimParcelSurveyQueryResponseDTO
from geoservice.model.dto.common import PointDTO
from geoservice.model.entity.Claim import Claim, ParcelClaim, RegisteredClaim
from geoservice.model.entity.Person import Person
from geoservice.service.claim_service import create_new_claim_request, query_claim_parcel, check_trace_id_exists, \
    query_parcel_claim_request, query_registered_parcel_claim_request, save_new_registered_parcel_claim_request
from geoservice.service.person_service import query_person
from geoservice.util.gis_util import is_polygon, load_shp_data, load_kml_data
from log.logger import logger

router = APIRouter()
log = logger()


@route(router=router, method="post", path="/claim_parcel", response_model=ClaimResponse)
# @dispatch(dispatch_event=None)
async def claim_parcel_api(request: Request, parcel_request: ClaimRequest = Depends()):
    body: ClaimRequestDTO = parcel_request.body
    content = None
    polygon = None
    content_type = None
    try:
        content, polygon, content_type = retrieve_claim_geometry(body)
    except ServiceException as e:
        raise e
    except Exception as e:
        log.error(e)
        raise ServiceException(ErrorCodes.CLAIM_POLYGON_FILE_NOT_PROCESSABLE)

    check_trace_id_exists(body.claim_trace_id)

    overlapping_response_dto_list: list[OverlappingResponseDTO] = validate_claim_parcel(polygon, body.srid,
                                                                                        body.state_code)
    claim_response_dto = ClaimResponseDTO(overlapping_parcels=overlapping_response_dto_list)

    for overlapping_response_dto in overlapping_response_dto_list:
        if overlapping_response_dto.is_documented:
            # do not create any claim and just report back
            header = Header(
                result_code=ErrorCodes.CLAIM_POLYGON_HAS_OVERLAP_WITH_DOCUMENTED_PARCEL.code,
                result_message=ErrorCodes.CLAIM_POLYGON_HAS_OVERLAP_WITH_DOCUMENTED_PARCEL.messsage_key
            )
            return handle_response(request, ClaimResponse(body=claim_response_dto, header=header))

    # TODO: should the overlapping report at the time also be included as well
    create_new_claim_request(content, content_type, polygon, body.claim_trace_id)
    return handle_response(request, ClaimResponse(body=claim_response_dto))


@route(router=router, method="post", path="/claim_parcel_query", response_model=ClaimParcelQueryResponse)
# @dispatch(dispatch_event=None)
async def claim_parcel_query_api(request: Request, claim_query_request: ClaimParcelQueryRequest = Depends()):
    body: ClaimParcelQueryRequestDTO = claim_query_request.body
    claim: Claim = query_claim_parcel(body)
    query_response_dto = ClaimParcelQueryResponseDTO(claim_trace_id=claim.claim_trace_id,
                                                     polygon=claim.claimed_polygon)
    response = ClaimParcelQueryResponse(body=query_response_dto)
    return handle_response(request, response)


def retrieve_claim_geometry(claim_request: ClaimRequestDTO):
    def check_len(obj):
        if len(obj) < 1:
            raise ServiceException(ErrorCodes.NO_FEATURE_FOUND)
        if len(obj) > 1:
            raise ServiceException(ErrorCodes.MULTIPLE_FEATURE_FOUND)

    content_type = claim_request.claimed_content_type.upper()
    content = None
    polygon = ""
    geometry = None

    if content_type == "GEOJSON":
        content = base64ToString(claim_request.claimed_content)
        geo_json = json.loads(content)
        features = geo_json["features"]
        check_len(features)

        feature = features[0]
        try:
            geometry_str = feature["geometry"]
            geometry = shape(geometry_str)
            polygon = geometry.wkt
        except KeyError:
            raise ServiceException(ErrorCodes.NO_GEOMETRY_FOUND)

    elif content_type == "SHP":
        content = base64.b64decode(claim_request.claimed_content)
        data_map = load_shp_data(content)
        check_len(data_map)
        data_tuple = data_map[0]
        geometry = data_tuple[0]
        polygon = geometry.wkt

    elif content_type == "KML":
        content = base64ToString(claim_request.claimed_content)
        geometries = load_kml_data(content)
        check_len(geometries)
        geometry = shape(geometries[0])
        polygon = geometry.wkt

    if geometry:
        if not is_polygon(geometry):
            raise ServiceException(ErrorCodes.INVALID_POLYGON_FOUND)
    else:
        raise ServiceException(ErrorCodes.NO_GEOMETRY_FOUND)

    return content, polygon, content_type


def validate_claim_parcel(polygon_wkt, srid, state_code):
    # 1- validate if polygon is in a containing cms polygon TODO: what if there are overlaps with multiple cms
    polygon_wrapper_req_dto = PolygonWrapperCmsDTO(state_code=state_code, polygon_wkt=polygon_wkt, srid=srid)
    wrapper_cms_req = WrapperCmsRequest(body=polygon_wrapper_req_dto, header=RequestHeader(params={}, lang="en_US"))

    wrapper_cms_response: WrapperCmsResponse = call_cadastre_api(wrapper_cms_req, WrapperCmsResponse,
                                                                 "/parcels/find_polygon_wrapper_cms")
    wrapper_cms = wrapper_cms_response.body
    if wrapper_cms is None or wrapper_cms['cms'] is None:
        raise ServiceException(ErrorCodes.CLAIM_POLYGON_NOT_FOUND_IN_STATES_CMS)

    # 2- check overlap with other layers, if overlap with documented parcels then error else report back
    # TODO: which layers must be excluded for the report?

    get_overlapping_req_dto = GetOverlappingParcelsDTO(state_code=state_code, polygon_wkt=polygon_wkt)
    get_overlapping_req = GetOverlappingParcelsRequest(body=get_overlapping_req_dto,
                                                       header=RequestHeader(params={}, lang="en_US"))
    overlapping_response: OverlappingResponse = call_cadastre_api(get_overlapping_req, OverlappingResponse,
                                                                  "/parcels/find_overlapping_parcels")
    overlapping_response_dto_list: list[OverlappingResponseDTO] = []
    for overlapping_response_dto in overlapping_response.body:
        polygon_wkt = overlapping_response_dto['polygonWkt']
        is_documented = overlapping_response_dto['isDocumented']
        cms = overlapping_response_dto['cms']
        overlapping_response_dto_list.append(
            OverlappingResponseDTO(is_documented=is_documented, cms=cms, polygon_wkt=polygon_wkt))

    return overlapping_response_dto_list


@route(router=router, method="post", path="/register_new_claim", response_model=RegisterNewClaimResponse)
async def register_new_claim_api(request: Request, register_new_claim_request: RegisterNewClaimRequest = Depends()):
    body: RegisterNewClaimRequestDTO = register_new_claim_request.body
    request_id = body.request_id
    neighborhood_point = body.neighborhood_point
    postal_code = body.postal_code
    area = body.area
    srs = None
    if neighborhood_point.srs:
        srs = neighborhood_point.srs
    else:
        srs = GLOBAL_SRID

    # 1- check duplicate request_id in database
    parcel_claims: List[ParcelClaim] = query_parcel_claim_request(request_id)
    if parcel_claims and parcel_claims[0].request_id:
        raise ServiceException(ErrorCodes.VALIDATION_CLAIM_REQUEST_ID_ALREADY_EXISTS)

    # 2- start claim process
    camunda_url = os.environ.get("CAMUNDA_URL", "http://localhost:7171/engine-rest")
    camunda_user = os.environ.get("CAMUNDA_USER", "demo")
    camunda_password = os.environ.get("CAMUNDA_PASSWORD", "demo")
    auth = requests.auth.HTTPBasicAuth(username=camunda_user, password=camunda_password)
    start_instance = StartInstance(
        url=camunda_url,
        key=os.environ.get("CLAIM_PARCEL_PROCESS_NAME", "Parcel_Claim_Process"),
        tenant_id=os.environ.get("CAMUNDA_TENANT_ID", 300)
    )
    start_instance.auth = auth
    start_instance.async_ = True  # Enable async execution
    start_instance.async_before = True  # Start before async continuation

    start_instance.add_variable(name="requestId", value=request_id)
    start_instance.add_variable(name="claimant", value=jsonable_encoder(body.claimant))
    start_instance.add_variable(name="surveyor", value=jsonable_encoder(body.surveyor))
    start_instance.add_variable(name="cms", value=body.cms)
    start_instance.add_variable(name="neighborhoodPoint", value=f'POINT({neighborhood_point.x} {neighborhood_point.y})')
    start_instance.add_variable(name="srs", value=str(srs))
    start_instance.add_variable(name="postalCode", value=str(postal_code))
    start_instance.add_variable(name="area", value=str(area))

    process_instance = start_instance()

    register_new_claim_response_dto = RegisterNewClaimResponseDTO(request_id=request_id)
    return handle_response(request, RegisterNewClaimResponse(body=register_new_claim_response_dto))


@route(router=router, method="post", path="/assign_surveyor_callback", response_model=RegisterNewClaimCallbackResponse)
async def assign_surveyor_callback_api(request: Request,
                                       register_new_claim_callback_request: RegisterNewClaimCallbackRequest = Depends()):
    body: RegisterNewClaimCallbackRequestDTO = register_new_claim_callback_request.body
    request_id = body.request_id

    # check if the survey result is already existing
    registered_claim: RegisteredClaim = query_registered_parcel_claim_request(RegisteredClaim(request_id=request_id))
    if registered_claim and registered_claim.request_id:
        raise ServiceException(ErrorCodes.CLAIM_SURVEY_RESULT_ALREADY_EXISTS)

    parcel_claim_request: ParcelClaim | None = None
    parcel_claim_requests: List[ParcelClaim] = query_parcel_claim_request(request_id=request_id)
    if not parcel_claim_requests:
        raise ServiceException(ErrorCodes.NO_CLAIM_FOUND)
    else:
        parcel_claim_request = parcel_claim_requests[0]

    # persist the survey result

    survey_parcel: str = body.survey_parcel
    geo_json = json.loads(survey_parcel)
    features = geo_json["features"]
    feature = features[0]
    geometry_str = feature["geometry"]
    geometry = shape(geometry_str)
    survey_parcel_wkt = geometry.wkt

    # claim_tracing_id = None
    # if not body.claim_tracing_id:
    #     claim_tracing_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100, 900)}"

    metadata: ParcelMetadataDTO = body.survey_parcel_metadata.metadata

    registered_claim = RegisteredClaim(request_id=request_id,
                                       claim_tracing_id=parcel_claim_request.claim_tracing_id,
                                       surveyor_id=parcel_claim_request.surveyor_id,
                                       cms=parcel_claim_request.cms,
                                       status=parse_to_int(body.status),
                                       area=parse_to_float(body.area),
                                       county=body.county,
                                       state_code=body.state_code,
                                       main_plate_number=body.main_plate_number,
                                       subsidiary_plate_number=body.subsidiary_plate_number,
                                       section=body.section,
                                       district=body.district,
                                       edges=json.dumps(jsonable_encoder(body.survey_parcel_metadata.edge_metadata)),
                                       beneficiary_rights=metadata.beneficiary_rights,
                                       accommodation_rights=metadata.accommodation_rights,
                                       is_apartment=metadata.is_apartment,
                                       floor_number=parse_to_float(metadata.floor_number),
                                       unit_number=parse_to_float(metadata.unit_number),
                                       orientation=parse_to_int(metadata.orientation, 8),
                                       polygon=survey_parcel_wkt,
                                       attachments=json.dumps(
                                           jsonable_encoder(body.survey_parcel_metadata.attachment_properties)))

    save_new_registered_parcel_claim_request(registered_claim)

    # proceed the camunda workflow
    camunda_url = os.environ.get("CAMUNDA_URL", "http://localhost:7171/engine-rest")
    camunda_user = os.environ.get("CAMUNDA_USER", "demo")
    camunda_password = os.environ.get("CAMUNDA_PASSWORD", "demo")
    auth = requests.auth.HTTPBasicAuth(username=camunda_user, password=camunda_password)

    correlation = CorrelateSingle(
        url=camunda_url,
        tenant_id=os.environ.get("CAMUNDA_TENANT_ID", 300),
        message_name=f"waitTomSurveyorResponse-{request_id}"
    )
    correlation.auth = auth
    try:
        results = correlation()
    except Exception as e:
        # TODO: why?
        log.error(e)

    register_new_claim_callback_response_dto = RegisterNewClaimCallbackResponseDTO(request_id=request_id)
    return handle_response(request, RegisterNewClaimCallbackResponse(body=register_new_claim_callback_response_dto))


@route(router=router, method="post", path="/claim_parcel_survey_query", response_model=ClaimParcelSurveyQueryResponse)
async def claim_parcel_survey_query_api(request: Request,
                                        claim_parcel_survey_query_request: ClaimParcelSurveyQueryRequest = Depends()):
    body: ClaimParcelSurveyQueryRequestDTO = claim_parcel_survey_query_request.body
    request_id = body.request_id
    claim_tracing_id = body.claim_tracing_id
    registered_claim: RegisteredClaim = query_registered_parcel_claim_request(
        RegisteredClaim(request_id=request_id, claim_tracing_id=claim_tracing_id))

    if not registered_claim:
        raise ServiceException(ErrorCodes.NO_CLAIM_FOUND)

    request_claim = None
    request_claims: List[ParcelClaim] = query_parcel_claim_request(request_id=registered_claim.request_id)
    if request_claims:
        request_claim = request_claims[0]

    polygon_coordinates = []
    if registered_claim.polygon:
        polygon = loads(registered_claim.polygon)
        if isinstance(polygon, Polygon):
            # Get coordinates and convert to list of [lon, lat] pairs
            polygon_coordinates = [list(coord) for coord in polygon.exterior.coords]

    parcel = {
        "type": "FeatureCollection",
        "name": "polygon_geojson",
        "features": {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon_coordinates] if polygon_coordinates else []
            },
            "properties": {
                "beneficiaryRights": registered_claim.beneficiary_rights,
                "accommodationRights": registered_claim.accommodation_rights,
                "isApartment": registered_claim.is_apartment,
                "floorNumber": registered_claim.floor_number,
                "unitNumber": registered_claim.unit_number,
                "orientation": registered_claim.orientation,
                "edges": [
                    {
                        "lineIndex": edge.get("lineIndex", ""),
                        "length": edge.get("length", ""),
                        "orientation": edge.get("orientation", ""),
                        "boundary": edge.get("boundary", ""),
                        "area": edge.get("area", ""),
                        "isAdjacentToPlateNumber": edge.get("isAdjacentToPlateNumber", ""),
                        "isAdjacentToPassage": edge.get("isAdjacentToPassage", ""),
                        "passageName": edge.get("passageName", ""),
                        "passageWidth": edge.get("passageWidth", ""),
                        "startingPoint": edge.get("startingPoint", ""),
                        "endingPoint": edge.get("startingPoint", "")
                    } for edge in json.loads(json.loads(registered_claim.edges))
                    if len(registered_claim.edges) > 0 and registered_claim.edges is not None
                ],
                "attachmentProperties": [
                    {
                        "title": attachment.get("title", ""),
                        "description": attachment.get("description", ""),
                        "attachmentCode": attachment.get("attachmentCode", ""),
                        "area": attachment.get("area", "")
                    } for attachment in json.loads(json.loads(registered_claim.attachments))
                    if len(registered_claim.attachments) > 0 and registered_claim.attachments is not None
                ]
            }
        }
    }

    neighbouring_point: PointDTO = PointDTO()
    neighbouring_point_shapely = loads(request_claim.neighbouring_point)
    neighbouring_point.x = neighbouring_point_shapely.x
    neighbouring_point.y = neighbouring_point_shapely.y

    claimants: List[Person] = query_person(Person(id=request_claim.claimant_id))
    surveyors: List[Person] = query_person(Person(id=request_claim.surveyor_id))

    claim_parcel_survey_query_response_dto = ClaimParcelSurveyQueryResponseDTO(
        request_id=request_id,
        claim_tracing_id=registered_claim.claim_tracing_id,
        cms=registered_claim.cms,
        area=registered_claim.area,
        neighborhood_point=neighbouring_point,
        county=registered_claim.county,
        state_code=registered_claim.state_code,
        main_plate_number=registered_claim.main_plate_number,
        subsidiary_plate_number=registered_claim.subsidiary_plate_number,
        section=registered_claim.section,
        district=registered_claim.district,
        parcel=parcel,
        claimant=PersonDTO.from_dict(jsonable_encoder(claimants[0])) if len(claimants) > 0 else None,
        surveyor=PersonDTO.from_dict(jsonable_encoder(surveyors[0])) if len(surveyors) > 0 else None
    )

    return handle_response(request, ClaimParcelSurveyQueryResponse(body=claim_parcel_survey_query_response_dto))
