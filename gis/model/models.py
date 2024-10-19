from enum import Enum
from abc import ABC

from shapely.geometry import Polygon, Point
from shapely.wkt import loads



class GeomType(Enum):
    POLYGON = "POLYGON"
    LINE = "LINE"
    POINT = "POINT"


class GISModel(ABC):
    
    def to_shapely(self):
        pass


class Point_T(GISModel):

    def __init__(self, x, y, srid="32638") -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.srid = srid
        
    def to_shapely(self):
        return loads(f'POINT ({self.x} {self.y})')


class Poly_T(GISModel):

    def __init__(self, wkt=None, srid="32638") -> None:
        super().__init__()
        self.wkt = wkt
        self.srid = srid
        
    def to_shapely(self):
        return loads(self.wkt)
