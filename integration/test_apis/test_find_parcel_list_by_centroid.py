import pytest
from fastapi.testclient import TestClient
from geoservice.app import app
from integration.test_apis.RequestBuilder import ParcelRequestBuilder as builder
client = TestClient(app)
headers = builder.build_headers("100:123")
params = builder.build_find_parcel_info_by_centroid(47.28788973, 33.21668853)

def test_find_parcel_list_by_centroid_200():
    response = client.get("/parcels/find_parcel_list_by_centroid", headers=headers,params=params)
    assert response.status_code == 200
    assert "geom" in response.json()["body"]["parcelGeomList"][0]

def test_find_parcel_list_by_centroid_10000():
    params.update({"distance": 10})
    response = client.get("/parcels/find_parcel_list_by_centroid", headers=headers,params=params)
    assert response.status_code == 200
    assert response.json()["body"]["parcelGeomList"] == []

#not implemented
"""def test_find_parcel_list_by_centroid_422():
    params = builder.build_wrong_find_parcel_info_by_centroid(47.28788973, 33.21668853)
    headers = builder.build_headers("100:123")
    response = client.get("/parcels/find_parcel_list_by_centroid", headers=headers,params=params)
    assert response.status_code == 422
    assert "missing" in response.json()["detail"][0]["type"]
"""