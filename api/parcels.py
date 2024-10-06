from service.poly_service import find_polygon_by_centroid
#from util.gis_util import transform_point
from common.constants import UTM_ZONE_38_SRID
from gis.model.models import Point_T
from .common import handle_response

from fastapi import APIRouter

router = APIRouter()

@router.get("/find_polygon_by_centroid")
def find_polygon_by_centroid_api(longtitude: float, latitude: float, srid="4326"):
    """
        lat/lon CRS is 4326
    """
    
    point = Point_T(longtitude, latitude, srid)
    # if srid != "4326":
    #     point = transform_point(point, "4326")
    geometry_wkt = find_polygon_by_centroid(point)
    
    return handle_response({"parcel": str(geometry_wkt)})
