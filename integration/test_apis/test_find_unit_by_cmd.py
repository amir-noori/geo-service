import pytest
from fastapi.testclient import TestClient
from geoservice.app import app
from integration.test_apis.RequestBuilder import ParcelRequestBuilder as builder
client = TestClient(app)

headers = builder.build_headers("100:123")
def test_find_unit_by_cmd_200():
    response = client.get("/unit/find_unit_by_cmd", headers=headers,params={"cms":"801"})
    assert response.status_code == 200
    assert "unitName" in response.json()["body"]

def test_find_unit_by_cmd_20002():
    response = client.get("/unit/find_unit_by_cmd", headers=headers,params={"cms":"8014"})
    assert response.status_code == 200
    assert response.json()["header"]["resultCode"] == 20002

def test_find_unit_by_cmd_422():
    response = client.get("/unit/find_unit_by_cmd", headers=headers)
    assert response.status_code == 422
    assert "missing" in response.json()["detail"][0]["type"]