from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from geoservice.common.constants import GLOBAL_SRID
from geoservice.model.dto.BaseDTO import partial_model


@partial_model
class PointDTO(BaseModel):
    x: float
    y: float
    srs: int = GLOBAL_SRID
    wkt: str

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True
    )
