from geoservice.model.dto.BaseDTO import BaseDTO, BaseResponse, partial_model
from geoservice.gis.model.models import GeomType
from geoservice.common.constants import GLOBAL_SRID


@partial_model
class ParcelInfoRequestDTO(BaseDTO):
    longtitude: float
    latitude: float
    srid: str
    distance: float

    def __init__(self, longtitude: str = None, latitude: str = None,
                 srid: str = "4326", distance: float = 10) -> None:
        super().__init__()
        self.longtitude = longtitude
        self.latitude = latitude
        self.srid = srid

        # TODO: must get value from system parameter
        if distance > 200:
            self.distance = 200
        else:
            self.distance = distance
        
    def get_service_key(self):
        return f"({self.longtitude},{self.latitude})"
