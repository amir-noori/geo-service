from geoservice.model.entity.common import BaseEntity
from geoservice.gis.model.models import Point_T


class ParcelRequestLog(BaseEntity):

    def __init__(self, id=None, national_id: str = None, first_name: str = None,
                 request_time=None, last_name: str = None, params: dict = {},
                 search_point: Point_T = None) -> None:

        self.id = id
        self.national_id = national_id
        self.first_name = first_name
        self.last_name = last_name
        self.request_time = request_time
        self.params = params
        self.search_point = search_point
