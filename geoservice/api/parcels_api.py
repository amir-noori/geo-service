import json
from datetime import datetime

import requests
from fastapi import APIRouter, Request, Depends

from common.ApplicationContext import ApplicationContext
from common.annotations import deprecated
from geoservice.api.common import handle_response
from geoservice.api.route import route
from geoservice.common.states import state_to_db_mapping
from geoservice.dispatcher.dispatcher import dispatch, get_header_for_dispatcher
from geoservice.event.Event import Event
from geoservice.gis.model.models import Poly_T
from geoservice.model.dto.ParcelDtoRequest import *
from geoservice.model.dto.ParcelDtoResponse import *
from geoservice.model.entity.ParcelRequestLog import ParcelRequestLog
from geoservice.service.parcel_request_log_service import save_parcel_req_log
from geoservice.service.parcel_service import *
from geoservice.util.common_util import get_state_code_by_name
from log.logger import logger

router = APIRouter()
log = logger()


def find_state_for_dispatch_get(event):
    log.debug(f"event data for dispatch {event['data']}")
    data = event["data"]["parcel_request_dto"]
    return find_state_for_dispatch(data)


def find_state_for_dispatch_post(event):
    log.debug(f"event data for dispatch {event['data']}")
    data = event["data"]["parcel_info_request"].body

    return find_state_for_dispatch(data)


def find_state_for_dispatch(data):
    longtitude = data.longtitude
    latitude = data.latitude
    srid = data.srid
    centroid = Point_T(longtitude, latitude, srid)
    for state_code, polygon in ApplicationContext.states_polygon_shape_map.items():
        if polygon.contains(centroid.to_shapely()):
            return state_code
    raise ServiceException(ErrorCodes.NO_STATE_FOUND)


def get_state_code(event):
    data = event["data"]
    return data["state_code"]


def load_states_polygons_list():
    state_polygon_map = {}
    header = get_header_for_dispatcher()

    # TODO: use call_all_service_providers
    for state_code, address in state_to_db_mapping.items():
        if address:
            address_split = address.split(":")
            ip = address_split[0]
            port = address_split[1]
            url = f"http://{ip}:{port}/parcels/find_state_polygon?state_code={state_code}"
            log.debug(f"calling URL: {url} to get state polygon.")
            try:
                response = requests.get(url, headers=header)
                if response.status_code == 200:
                    response_dict = json.loads(
                        response.content.decode('utf-8'))
                    poly = Poly_T(
                        wkt=response_dict['body']['geom'], srid=GLOBAL_SRID)
                    state_polygon_map[state_code] = poly.to_shapely()

                else:
                    log.debug(f"{response.status_code} , {response.content}")
            except Exception as e:
                log.error_bold(f"""                        
                        error connecting to server {url}
                        Exception: {e}
                      """)

    ApplicationContext.states_polygon_shape_map = state_polygon_map
    return {}


# @router.get("/find_parcel_list_by_centroid", response_model=ParcelListResponse)
@route(router=router, method="get", path="/find_parcel_list_by_centroid", response_model=ParcelListResponse)
@dispatch(dispatch_event=Event(find_state_for_dispatch_get))
def find_parcel_list_by_centroid_api(request: Request, parcel_request_dto: ParcelInfoRequestDTO = Depends()):
    point = Point_T(parcel_request_dto.longtitude,
                    parcel_request_dto.latitude,
                    parcel_request_dto.srid)
    polygon_list, buffer = find_parcel_list_by_centroid(
        point, parcel_request_dto.distance)

    parcel_geom_list = []
    for polygon in polygon_list:
        parcel_geom = ParcelGeomDTO(
            geom=polygon, type=GeomType.POLYGON, crs=GLOBAL_SRID)
        parcel_geom_list.append(parcel_geom)

    buffer_geom = ParcelGeomDTO(
        geom=buffer, type=GeomType.POLYGON, crs=GLOBAL_SRID)
    parcel_list_dto = ParcelListDTO(
        parcel_geom_list=parcel_geom_list, buffer_geom=buffer_geom)
    parcel_list_response = ParcelListResponse(body=parcel_list_dto)

    return handle_response(request, parcel_list_response)


# @router.get("/find_parcel_info_by_centroid", response_model=ParcelInfoResponse)
@deprecated("use post version")
@route(router=router, method="get", path="/find_parcel_info_by_centroid", response_model=ParcelInfoResponse)
@dispatch(dispatch_event=Event(find_state_for_dispatch_get))
def find_parcel_info_by_centroid_api_get(request: Request,
                                         parcel_request_dto: ParcelInfoRequestDTO = Depends()):
    point = Point_T(parcel_request_dto.longtitude,
                    parcel_request_dto.latitude,
                    parcel_request_dto.srid)
    parcel = find_parcel_info_by_centroid(point)
    parcel_info = assemble_parcel_info_response(parcel)
    response = ParcelInfoResponse(parcel_info)
    return handle_response(request, response)


@route(router=router, method="post", path="/find_parcel_info_by_centroid", response_model=ParcelInfoResponse)
@dispatch(dispatch_event=Event(find_state_for_dispatch_post))
def find_parcel_info_by_centroid_api_post(request: Request,
                                          parcel_info_request: ParcelInfoRequest = Depends()):
    centroid: CentoridDTO = parcel_info_request.body
    header: RequestHeader = parcel_info_request.header
    point = Point_T(centroid.longtitude,
                    centroid.latitude,
                    centroid.srid)
    parcel = find_parcel_info_by_centroid(point)
    parcel_info = assemble_parcel_info_response(parcel)

    national_id = None
    first_name = None
    last_name = None

    try:
        national_id = header.params['nationalId']
    except KeyError:
        pass

    try:
        first_name = header.params['firstName']
    except KeyError:
        pass

    try:
        last_name = header.params['lastName']
    except KeyError:
        pass

    parcel_request_log = ParcelRequestLog(
        national_id=national_id,
        first_name=first_name,
        last_name=last_name,
        request_time=datetime.now(),
        search_point=point
    )
    save_parcel_req_log(parcel_request_log)

    response = ParcelInfoResponse(parcel_info)
    return handle_response(request, response)


@router.get("/find_state_polygon", response_model=ParcelGeomDTO)
# @route(router=router, method="get", path="/find_state_polygon", response_model=ParcelGeomDTO)
@dispatch(dispatch_event=Event(get_state_code))
def find_state_polygon_api(request: Request, state_code: str):
    parcel = find_state_polygon(state_code)
    parcel_geom_dto = ParcelGeomDTO(geom=parcel.polygon)
    state_polygon_response = StatePolygonResponse(body=parcel_geom_dto)
    return handle_response(request, state_polygon_response)


@route(router=router, method="post", path="/find_polygon_wrapper_cms", response_model=WrapperCmsResponse)
@dispatch(dispatch_event=Event(get_state_code))
def find_polygon_wrapper_cms_api(request: Request, wrapper_cms_request: WrapperCmsRequest = Depends()):
    polygon_wrapper_cms_req = wrapper_cms_request.body
    cms_unit = find_polygon_wrapper_cms(polygon_wrapper_cms_req.polygon_wkt)
    if cms_unit is None or not cms_unit.cms:
        raise ServiceException(ErrorCodes.NO_CONTAINING_CMS_FOUND)

    response_dto = WrapperCmsResponseDTO(cms=cms_unit.cms, cms_polygon_wkt=cms_unit.polygon_wkt)
    response = WrapperCmsResponse(body=response_dto)
    return handle_response(request, response)


@route(router=router, method="post", path="/find_overlapping_parcels", response_model=OverlappingResponse)
@dispatch(dispatch_event=Event(get_state_code))
def find_overlapping_parcels_api(request: Request,
                                 overlapping_parcels_request: GetOverlappingParcelsRequest = Depends()):
    overlapping_parcels_req_dto = overlapping_parcels_request.body
    overlapping_parcels = find_overlapping_parcels_by_polygon(overlapping_parcels_req_dto.polygon_wkt)

    response_dto_list = []
    for parcel in overlapping_parcels:
        overlapping_dto = OverlappingResponseDTO(polygon_wkt=str(parcel.polygon), cms=parcel.cms,
                                                 layer_name=parcel.layer_name, is_documented=parcel.is_documented)
        response_dto_list.append(overlapping_dto)

    response = OverlappingResponse(body=response_dto_list)
    return handle_response(request, response)


@route(router=router, method="get", path="/get_states_polygons")
def get_states_polygons_api(request: Request):
    load_states_polygons_list()
    return {}


def assemble_parcel_info_response(parcel) -> ParcelInfoDTO:
    log.debug(f"assembling parcel {parcel}")
    deed = parcel.deed
    state = deed.state
    state_code = get_state_code_by_name(state)

    apartments = []

    if deed.deed_parts:
        for part in deed.deed_parts:
            apartment_metadata = ParcelMetadataDTO(subsidiary_plate_number=part.subsidiary_plate_number,
                                                   partitioned=deed.subsidiary_plate_number,
                                                   segment=deed.segment,
                                                   area=part.legal_area)
            apartments.append(apartment_metadata)

    common_metadata = ParcelMetadataDTO(state=state,
                                        state_code=state_code,
                                        cms=deed.cms,
                                        section=deed.section,
                                        district=deed.district,
                                        main_plate_number=deed.main_plate_number)

    parcel_geom = ParcelGeomDTO(geom=str(parcel.polygon),
                                type=GeomType.POLYGON,
                                crs="ESPG:4326"  # TODO: static value for now, but should be dynamic later
                                )

    ground_metadata = ParcelMetadataDTO(subsidiary_plate_number=deed.subsidiary_plate_number,
                                        partitioned=deed.partitioned,
                                        segment=deed.segment,
                                        area=deed.legal_area)

    parcel_ground = ParcelGroundDTO(parcel_geom=parcel_geom,
                                    metadata=ground_metadata)

    parcel_info = ParcelInfoDTO(common_metadata=common_metadata,
                                ground=parcel_ground,
                                apartments=apartments)

    return parcel_info
