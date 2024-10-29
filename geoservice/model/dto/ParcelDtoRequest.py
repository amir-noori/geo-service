from geoservice.model.dto.BaseDTO import BaseDTO, RequestHeader, partial_model
from geoservice.common.constants import GLOBAL_SRID
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from pydantic import Field, BaseModel, field_validator
from typing import Optional, Any
from geoservice.exception.service_exception import ValidationException
from geoservice.exception.common import ErrorCodes


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


class CentoridDTO(BaseModel):

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    longtitude: float
    latitude: float
    srid: Optional[str] = Field(str(GLOBAL_SRID))
    distance: Optional[float] = Field(10, ge=1, le=200)

    def get_service_key(self):
        return f"({self.longtitude},{self.latitude})"


class ParcelInfoRequest(BaseModel):

    body: CentoridDTO
    header: RequestHeader
    
    @field_validator('header')
    @classmethod
    def ensure_foobar(cls, h: Any):
        try:
            if not h.params['nationalId']:
                raise ValidationException(ErrorCodes.VALIDATION_NATIONAL_ID_REQUIRED)
        except KeyError:
            raise ValidationException(ErrorCodes.VALIDATION_NATIONAL_ID_REQUIRED)
        
        return h

    def get_service_key(self):
        service_key = f"nationalId:{self.header.params['nationalId']}, Centroid({self.body.latitude},{self.body.latitude})"
        return service_key
