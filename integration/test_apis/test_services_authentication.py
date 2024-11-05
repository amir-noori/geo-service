import pytest
from fastapi.testclient import TestClient
from geoservice.app import app
from integration.test_apis.RequestBuilder import ParcelRequestBuilder as builder
client = TestClient(app)
headers = builder.build_headers("100:123")
wrong_headers = builder.build_headers("1004:123")
post_content = builder.build_find_parcel_info_post_content("123123", "asdad", "asdasd", 47.28788973, 33.21668853)
get_params = builder.build_find_parcel_info_by_centroid(47.28788973, 33.21668853)

def test_find_parcel_info_by_centroid_401():
    response = client.get("/parcels/find_parcel_info_by_centroid", headers=wrong_headers,params=get_params)
    assert response.status_code == 401
    assert "not authorized" in response.json()["header"]["result_message"]

def test_find_parcel_info_by_centroid_post_401():
    response = client.post("/parcels/find_parcel_info_by_centroid", headers=wrong_headers,json=post_content)
    assert response.status_code == 401
    assert "not authorized" in response.json()["header"]["result_message"]

#this service authentication is not enabled
def test_find_unit_by_cmd_200():
    response = client.get("/unit/find_unit_by_cmd", headers=wrong_headers,params={"cms":"802"})
    assert response.status_code == 200
    #assert "not authorized" in response.json()["header"]["result_message"]