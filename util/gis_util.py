# from osgeo import ogr
# from osgeo import osr

from shapely.wkt import loads
from shapely.geometry import Polygon, Point

from gis.model.models import Point_T, Poly_T


def poly_contains_point(poly: Poly_T, point: Point_T):
    return poly.to_shapely().contains(point.to_shapely())


# def transform_point(p: Point_T, to_srid):

#     point = ogr.Geometry(ogr.wkbPoint)
#     point.AddPoint(p.x, p.y)

#     inSpatialRef = osr.SpatialReference()
#     inSpatialRef.ImportFromEPSG(p.srid)

#     outSpatialRef = osr.SpatialReference()
#     outSpatialRef.ImportFromEPSG(to_srid)

#     coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

#     point.Transform(coordTransform)

#     return Point_T(point.GetX(), point.GetY(), to_srid)
