import pytest
from fastapi.testclient import TestClient
from fastapi import status
from geoservice.app import app
from geoservice.common.constants import *
from geoservice.tests.RequestBuilder import ParcelRequestBuilder as builder
client = TestClient(app)
headers = builder.build_headers(AUTH_HEADER)
wrong_headers = builder.build_headers(WRONG_AUTH_HEADER)
post_content = builder.build_find_parcel_info_post_content(NATIONAL_ID, F_NAME, L_NAME, LON, LAT)
get_params = builder.build_find_parcel_info_by_centroid(LON, LAT)

def test_find_parcel_info_by_centroid_http_resp_401():
    response = client.get("/parcels/find_parcel_info_by_centroid", headers=wrong_headers,params=get_params)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_find_parcel_info_by_centroid_post_http_resp_401():
    response = client.post("/parcels/find_parcel_info_by_centroid", headers=wrong_headers,json=post_content)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED