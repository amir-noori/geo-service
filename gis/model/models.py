from enum import Enum


class GeomType(Enum):
    POLYGON = "POLYGON"
    LINE = "LINE"
    POINT = "POINT"


class GISModel:
    pass


class Point_T(GISModel):

    def __init__(self, x, y, srid="32638") -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.srid = srid
