from service.parcel_service import *
# from util.gis_util import transform_point
from common.constants import UTM_ZONE_38_SRID
from gis.model.models import Point_T
from .common import handle_response
from util.common_util import get_state_code_by_name
from model.dto.ParcelDTO import *
from event.Event import Event
from common.ApplicationContext import ApplicationContext
from fastapi import APIRouter, Request
from dispatcher.dispatcher import dispatch
from exception.common import ErrorCodes
from common.states import state_to_db_mapping
from gis.model.models import Poly_T
import requests


router = APIRouter()


def find_state_for_dispatch(event):
    data = event["data"]
    longtitude = data["longtitude"]
    latitude = data["latitude"]
    srid = data["srid"]
    centroid = Point_T(longtitude, latitude, srid)

    for state_code, polygon in ApplicationContext.states_polygon_shape_map.items():
        if polygon.contains(centroid.to_shapely()):
            return state_code
    raise ServiceException(ErrorCodes.NO_STATE_FOUND)


def get_state_code(event):
    data = event["data"]
    return data["state_code"]


@router.get("/find_polygon_by_centroid")
@dispatch
def find_polygon_by_centroid_api(request: Request, longtitude: float, latitude: float, srid="4326"):
    """
        lat/lon CRS is 4326
    """

    point = Point_T(longtitude, latitude, srid)
    # if srid != "4326":
    #     point = transform_point(point, "4326")
    geometry_wkt = find_polygon_by_centroid(point)

    return handle_response({"parcel": str(geometry_wkt)})


@router.get("/find_parcel_info_by_centroid", response_model=ParcelInfoResponse)
@dispatch(dispatch_event=Event(find_state_for_dispatch))
def find_parcel_info_by_centroid_api(request: Request, longtitude: float, latitude:
                                     float, srid="4326"):
    point = Point_T(longtitude, latitude, srid)
    parcel = find_parcel_info_by_centroid(point)
    parcel_info = assemble_parcel_info_response(parcel)
    response = ParcelInfoResponse(parcel_info)
    return handle_response(response)


@router.get("/find_state_polygon", response_model=ParcelGeomDTO)
@dispatch(dispatch_event=Event(get_state_code))
def find_state_polygon_api(request: Request, state_code: str):
    parcel = find_state_polygon(state_code)
    parcel_dto = ParcelGeomDTO(geom=parcel.polygon)
    return handle_response(parcel_dto)


@router.get("/get_states_polygons")
def get_states_polygons_api(request: Request):
    state_polygon_map = {}
    for state_code, address in state_to_db_mapping.items():
        address_split = address.split(":")
        ip = address_split[0]
        port = address_split[1]
        url = f"http://{ip}:{port}/parcels/find_state_polygon?state_code={state_code}"
        print(f"calling URL: {url} to get state polygon.")
        response = requests.get(url)
        if response.status_code == 200:
            state_polygon = json.loads(response.content.decode('utf-8'))
            wkt = state_polygon['geom']

            response_dict = json.loads(response.content)
            poly = Poly_T(wkt=response_dict['geom'], srid=GLOBAL_SRID)
            state_polygon_map[state_code] = poly.to_shapely()

        else:
            print(response.status_code, response)

    ApplicationContext.states_polygon_shape_map = state_polygon_map
    return {}


def assemble_parcel_info_response(parcel) -> ParcelInfoDTO:
    print(f"assembling parcel {parcel}")
    deed = parcel.deed
    state = deed.state
    state_code = get_state_code_by_name(state)

    apartments = []

    if deed.deed_parts:
        for part in deed.deed_parts:
            apartment_metadata = ParcelMetadataDTO(subsidiary_plate_number=part.subsidiary_plate_number,
                                                   partitioned=deed.partitioned,
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
