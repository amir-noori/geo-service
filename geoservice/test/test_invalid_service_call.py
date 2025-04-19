import pytest
from fastapi.testclient import TestClient
from geoservice.app import app
from geoservice.common.constants import *
from geoservice.tests.RequestBuilder import ParcelRequestBuilder as builder
from fastapi import status
client = TestClient(app)

def test_find_polygon_by_centroid_http_resp_503():
    params = builder.build_find_parcel_info_by_centroid(LON, LAT)
    response = client.get("/parcels/find_polygon_by_centroid", params=params)
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
