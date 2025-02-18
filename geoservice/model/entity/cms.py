from geoservice.model.entity.common import BaseEntity


class CmsUnit(BaseEntity):
    polygon_wkt: str
    cms: str

    def __init__(self, cms=None, polygon_wkt=None) -> None:
        self.polygon_wkt = polygon_wkt
        self.cms = cms
