import pytest
from fastapi.testclient import TestClient
from fastapi import status
from geoservice.app import app
from geoservice.tests.RequestBuilder import ParcelRequestBuilder as builder
from geoservice.common.constants import *
from geoservice.exception.common import ErrorCodes
import copy

client = TestClient(app)
headers = builder.build_headers(AUTH_HEADER)
getParams = builder.build_find_parcel_info_by_centroid(LON, LAT)
post_params = builder.build_find_parcel_info_post_content(national_id=NATIONAL_ID, first_name=F_NAME,last_name= L_NAME,longitude= LON,latitude= LAT)
wrong_post_content = builder.build_wrong_find_parcel_info_post_content(NATIONAL_ID, F_NAME, L_NAME, LON, LAT)

def test_find_state_polygon_http_resp_200():
    params = {
        "state_code": "8"
    }
    response = client.get("/parcels/find_state_polygon",headers=headers ,params=params)
    assert response.status_code == status.HTTP_200_OK
    assert "geom" in response.json()["body"] 


def test_find_parcel_info_by_centroid_http_resp_200():
    response = client.get("/parcels/find_parcel_info_by_centroid", headers=headers,params=getParams)
    assert response.status_code == status.HTTP_200_OK
    assert "parcelGeom" in response.json()["body"]["ground"]

def test_find_parcel_list_by_centroid_http_resp_200():
    response = client.get("/parcels/find_parcel_list_by_centroid", headers=headers,params=getParams)
    assert response.status_code == status.HTTP_200_OK
    assert "geom" in response.json()["body"]["parcelGeomList"][0] 

def test_find_parcel_info_by_centroid_empty_resp_10000():
    getParams.update({"longtitude": 10})
    response = client.get("/parcels/find_parcel_info_by_centroid", headers=headers,params=getParams)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["header"]["resultCode"] == ErrorCodes.NO_PARCEL_FOUND.code

def test_find_parcel_list_by_centroid_empty_resp_10000():
    getParams.update({"longtitude": 10000})
    response = client.get("/parcels/find_parcel_list_by_centroid", headers=headers,params=getParams)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["body"]["parcelGeomList"] == []

def test_find_parcel_info_by_centroid_post_http_resp_200():
    response = client.post("/parcels/find_parcel_info_by_centroid", headers=headers,json=post_params)
    assert response.status_code == status.HTTP_200_OK


# Request Validation tests
def test_find_parcel_info_by_centroid_post_auth_resp_422():
    response = client.post("/parcels/find_parcel_info_by_centroid", headers=headers,json=wrong_post_content)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "missing" in response.json()["detail"][0]["type"]

def test_find_parcel_info_by_centroid_post_validation_resp_3000():
    copyParams = copy.deepcopy(post_params)
    copyParams["header"]["params"]["nationalId"] = ""
    response = client.post("/parcels/find_parcel_info_by_centroid", headers=headers,json=copyParams)
    print(copyParams)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["header"]["resultCode"] == ErrorCodes.VALIDATION_NATIONAL_ID_REQUIRED.code

def test_find_parcel_info_by_centroid_post_validation_resp_3001():
    copyParams = copy.deepcopy(post_params)
    copyParams["header"]["params"]["firstName"] = ""
    response = client.post("/parcels/find_parcel_info_by_centroid", headers=headers,json=copyParams)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["header"]["resultCode"] == ErrorCodes.VALIDATION_FIRST_NAME_REQUIRED.code

def test_find_parcel_info_by_centroid_post_validation_resp_3002():
    copyParams = copy.deepcopy(post_params)
    copyParams["header"]["params"]["lastName"] = ""
    response = client.post("/parcels/find_parcel_info_by_centroid", headers=headers,json=copyParams)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["header"]["resultCode"] == ErrorCodes.VALIDATION_LAST_NAME_REQUIRED.code

