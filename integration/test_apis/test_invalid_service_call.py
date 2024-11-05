import pytest
from fastapi.testclient import TestClient
from geoservice.app import app
from integration.test_apis.RequestBuilder import ParcelRequestBuilder as builder
client = TestClient(app)

def test_invalid_service_name():
    headers = builder.build_headers("100:123")
    params = builder.build_find_parcel_info_by_centroid(47.28788973, 33.21668853)
    response = client.get("/parcels/find_parcl_service", headers=headers, params=params)
    assert response.status_code == 503
    #assert "parcel" in response.json()  

def test_find_polygon_by_centroid():
    params = builder.build_find_parcel_info_by_centroid(47.28788973, 33.21668853)
    response = client.get("/parcels/find_polygon_by_centroid", params=params)
    assert response.status_code == 503
    #assert "parcel" in response.json()