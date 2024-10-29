from geoservice.model.dto.BaseDTO import BaseDTO, RequestHeader, partial_model, BaseRequest
from geoservice.gis.model.models import GeomType
from geoservice.common.constants import GLOBAL_SRID
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


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


@partial_model
class CentoridDTO(BaseModel):

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

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


@partial_model
class ParcelInfoRequest(BaseModel):

    body: CentoridDTO
    header: RequestHeader

    # def __init__(self, header, body) -> None:
    #     super().__init__()
    #     self.body = body
    #     self.header = header

    def get_service_key(self):
        print("header -> ", self.header)
        print("body -> ", self.body)
        service_key = f"nationalId:{self.header.params['nationalId']}, Centroid({self.body.latitude},{self.body.latitude})"
        print(f"service_key: {service_key}")
        return service_key
