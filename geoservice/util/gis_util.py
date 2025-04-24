# from osgeo import ogr
# from osgeo import osr

import os
import tempfile
import uuid
from zipfile import ZipFile
from pykml import parser
import fiona
from shapely import union_all
from shapely.geometry import shape
from shapely import wkt
from shapely.wkt import loads
from shapely.geometry import Point, LineString, Polygon
from geoservice.gis.model.models import Point_T, Poly_T


def poly_contains_point(poly: Poly_T, point: Point_T):
    return poly.to_shapely().contains(point.to_shapely())


def union_polygons_by_wkt(polygon_list: list[str]):
    poly_list = []
    for poly_wkt in polygon_list:
        poly = loads(poly_wkt)
        poly_list.append(poly)
    return union_all(poly_list)

def load_kml_data(kml_string):
    geometries = []
    kml_doc = parser.fromstring(kml_string.encode('utf-8'))
    placemark = kml_doc.Document.Folder.Placemark
    for child in placemark.MultiGeometry.getchildren():
        if child.tag.endswith('Polygon'):
            # Extract coordinates for Polygon
            coords = child.outerBoundaryIs.LinearRing.coordinates.text.strip().split()
            polygons = [tuple(map(float, c.split(','))) for c in coords]
            geometries.append(Polygon(polygons))
        elif child.tag.endswith('Point'):
            # Extract coordinates for Point
            coords = child.coordinates.text.strip().split(',')
            point = tuple(map(float, coords))
            geometries.append(Point(point))
        elif child.tag.endswith('LineString'):
            # Extract coordinates for LineString
            coords = child.coordinates.text.strip().split()
            lines = [tuple(map(float, c.split(','))) for c in coords]
            geometries.append(LineString(lines))

    return geometries


def load_shp_data(binary_data):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save the binary data to a temporary ZIP file
        filename = str(uuid.uuid4()) + ".zip"
        temp_zip_path = os.path.join(temp_dir, filename)
        with open(temp_zip_path, "wb") as f:
            f.write(binary_data)

        # Extract the ZIP file
        with ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Find the .shp file in the extracted files
        shp_file = None
        for file in os.listdir(temp_dir):
            if file.endswith(".shp"):
                shp_file = os.path.join(temp_dir, file)
                break

        if not shp_file:
            raise FileNotFoundError("No .shp file found in the extracted data.")

        # Open the Shapefile using Fiona
        data_map = {}
        with fiona.open(shp_file) as src:
            # Iterate over each feature in the Shapefile
            index = 0
            for feature in src:
                # Convert the feature's geometry to a Shapely geometry
                geom = shape(feature['geometry'])

                # Access the feature's properties (attributes)
                properties = feature['properties']

                data_map[index] = (geom, properties)

                index = index + 1

        return data_map


def is_polygon(geom):
    """
        geom: is of shapely geometry
    """
    geom_type = geom.geom_type
    return geom_type == "MultiPolygon" or geom_type == "Polygon"


def polygon_wkt_to_oracle_sdo_geometry(polygon_wkt, srid=4326):
    # Parse WKT to Shapely Polygon
    polygon = wkt.loads(polygon_wkt)

    # Get exterior coordinates and flatten into a single list
    coords = []
    for x, y in polygon.exterior.coords:
        coords.extend([str(x), str(y)])

    # Build the Oracle query
    oracle_query = f"""SDO_GEOMETRY(
      2003,        -- 2D polygon
      {srid},      -- SRID
      NULL,        -- No point data for polygons
      SDO_ELEM_INFO_ARRAY(1, 1003, 1),  -- 1003 = exterior polygon ring
      SDO_ORDINATE_ARRAY(
        {', '.join(coords)}     -- Polygon vertices
      )
    )
    """

    return oracle_query

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
