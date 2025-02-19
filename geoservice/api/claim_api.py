import base64
import json

from fastapi import APIRouter, Depends
from fastapi import Request
from shapely.geometry import shape

from common.str_util import base64ToString
from geoservice.api.common import handle_response
from geoservice.api.route import route
from geoservice.api.utils import call_cadastre_api
from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ServiceException
from geoservice.model.dto.BaseDTO import Header
from geoservice.model.dto.BaseDTO import RequestHeader
from geoservice.model.dto.ParcelDtoRequest import PolygonWrapperCmsDTO, WrapperCmsRequest, GetOverlappingParcelsDTO, \
    GetOverlappingParcelsRequest
from geoservice.model.dto.ParcelDtoResponse import WrapperCmsResponse, OverlappingResponse, OverlappingResponseDTO
from geoservice.model.dto.claim.ClaimDtoReq import ClaimRequest, ClaimParcelQueryRequest
from geoservice.model.dto.claim.ClaimDtoReq import ClaimRequestDTO, ClaimParcelQueryRequestDTO
from geoservice.model.dto.claim.ClaimDtoResponse import ClaimResponse, ClaimParcelQueryResponse, \
    ClaimParcelQueryResponseDTO, ClaimResponseDTO
from geoservice.model.entity.Claim import Claim
from geoservice.service.claim_service import create_new_claim_request, query_claim_parcel, check_trace_id_exists
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

    overlapping_response_dto_list: list[OverlappingResponseDTO] = validate_claim_parcel(polygon, body.srid, body.state_code)
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
