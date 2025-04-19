from geoservice.common.constants import GLOBAL_SRID

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class PointDTO(BaseModel):

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True
    )

    def __init__(self, x, y, srs=GLOBAL_SRID, wkt=None) -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.srs = srs
        self.wkt = wkt