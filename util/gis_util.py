from osgeo import ogr
from osgeo import osr

from gis.model.models import Point_T


def transform_point(p: Point_T, to_srid):

    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(p.x, p.y)

    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(p.srid)

    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(to_srid)

    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    point.Transform(coordTransform)

    return Point_T(point.GetX(), point.GetY(), to_srid)
