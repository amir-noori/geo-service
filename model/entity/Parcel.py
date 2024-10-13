from enum import Enum
import json

from gis.model.models import Point_T
from util.object_util import toJSON

class Direction(Enum):
    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4




class BaseEntity:
    
    def toJSON(self):
        return toJSON(self)
    

class Deed(BaseEntity):
    
    volume_code: str
    volume_number: str
    page_number: str
    main_plate_number: str
    subsidiary_plate_number: str
    cms: str
    segment: str
    section: str
    district: str
    partitioned: str
    legal_area: str
    address_text: str
    state: str
    deed_parts: list

    def __init__(self, volume_code=None, volume_number=None, page_number=None,
                 main_plate_number=None, subsidiary_plate_number=None, segment=None,
                 cms=None, section=None, district=None, partitioned=None,
                 legal_area=None, address_text=None, state=None, deed_parts=None) -> None:
        """
            volume_code: code seri daftar
            volume_number: shomare daftar
            page_number: shomare safheh
            section: bakhsh
            district: nahieh
            partitioned: mafroozi
            segment: gheteh
        """
        self.volume_code = volume_code
        self.volume_number = volume_number
        self.page_number = page_number
        self.main_plate_number = main_plate_number
        self.subsidiary_plate_number = subsidiary_plate_number
        self.cms = cms
        self.segment = segment
        self.section = section
        self.district = district
        self.partitioned = partitioned
        self.legal_area = legal_area
        self.address_text = address_text
        self.state = state
        self.deed_parts = deed_parts

    def get_location_code(self):
        """
            location_code : code mahale voghou
        """
        if not self.cms or not self.section or self.district:
            return None

        return f"{self.cms}{self.section}{self.district}"


class DeedPart(BaseEntity):

    def __init__(self, volume_code=None, volume_number=None, page_number=None,
                 legal_area=None, subsidiary_plate_number=None,
                 segment=None, partitioned=None, cms=None) -> None:
        
        self.volume_code = volume_code
        self.volume_number = volume_number
        self.page_number = page_number
        self.legal_area = legal_area
        self.subsidiary_plate_number = subsidiary_plate_number
        self.segment = segment
        self.partitioned = partitioned
        self.cms=cms


class CardinalRecord(BaseEntity):

    def __init__(self, lenght, cardinal: Direction, direction: Direction) -> None:
        self.lenght = lenght
        self.cardinal = cardinal
        self.direction = direction


class Parcel(BaseEntity):
    
    polygon: str
    centroid: Point_T
    cardinals: str
    deed: Deed
    cms: str
    area: str

    def __init__(self, polygon=None, centroid: Point_T = None, deed: Deed = None,
                 cardinals=None, cms=None, area=None) -> None:
        self.polygon = polygon
        self.centroid = centroid
        self.cardinals = cardinals
        self.deed = deed
        self.cms = cms
        self.area = area
