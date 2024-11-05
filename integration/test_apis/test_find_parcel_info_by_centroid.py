import pytest
from fastapi.testclient import TestClient
from geoservice.app import app
from integration.test_apis.RequestBuilder import ParcelRequestBuilder as builder
import copy

client = TestClient(app)
headers = builder.build_headers("100:123")
getParams = builder.build_find_parcel_info_by_centroid(46.4178533, 33.6289384)
post_params = builder.build_find_parcel_info_post_content(national_id="123123", first_name="Johnny",last_name= "Walker",longitude= 46.4178533,latitude= 33.6289384)
wrong_post_content = builder.build_wrong_find_parcel_info_post_content("123123", "Johnny", "Walker", 46.4178533, 33.6289384)

def test_find_parcel_info_by_centroid_200():
    response = client.get("/parcels/find_parcel_info_by_centroid", headers=headers,params=getParams)
    assert response.status_code == 200
    assert "parcelGeom" in response.json()["body"]["ground"]

def test_find_parcel_info_by_centroid_10000():
    getParams.update({"longtitude": 10})
    response = client.get("/parcels/find_parcel_info_by_centroid", headers=headers,params=getParams)
    assert response.status_code == 200
    assert response.json()["header"]["resultCode"] == 10000
    #assert "parcelGeom" in response.json()["body"]["ground"]

def test_find_parcel_info_by_centroid_post_200():
    response = client.post("/parcels/find_parcel_info_by_centroid", headers=headers,json=post_params)
    assert response.status_code == 200
    #assert "parcelGeom" in response.json()["body"]["ground"]

def test_find_parcel_info_by_centroid_post_422():
    response = client.post("/parcels/find_parcel_info_by_centroid", headers=headers,json=wrong_post_content)
    assert response.status_code == 422
    assert "missing" in response.json()["detail"][0]["type"]

def test_find_parcel_info_by_centroid_post_3000():
    copyParams = copy.deepcopy(post_params)
    copyParams["header"]["params"]["nationalId"] = ""
    response = client.post("/parcels/find_parcel_info_by_centroid", headers=headers,json=copyParams)
    print(copyParams)
    assert response.status_code == 422
    assert response.json()["header"]["resultCode"] == 3000
    #assert "missing" in response.json()["detail"][0]["type"]

def test_find_parcel_info_by_centroid_post_3001():
    copyParams = copy.deepcopy(post_params)
    copyParams["header"]["params"]["firstName"] = ""
    print("******************")
    print(copyParams)
    response = client.post("/parcels/find_parcel_info_by_centroid", headers=headers,json=copyParams)
    assert response.status_code == 422
    assert response.json()["header"]["resultCode"] == 3001

def test_find_parcel_info_by_centroid_post_3002():
    copyParams = copy.deepcopy(post_params)
    copyParams["header"]["params"]["lastName"] = ""
    print("******************")
    print(copyParams)
    response = client.post("/parcels/find_parcel_info_by_centroid", headers=headers,json=copyParams)
    assert response.status_code == 422
    assert response.json()["header"]["resultCode"] == 3002