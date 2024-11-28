import pytest
from fastapi.testclient import TestClient
from fastapi import status
from geoservice.app import app
from geoservice.common.constants import AUTH_HEADER
from geoservice.exception.common import ErrorCodes
from geoservice.tests.RequestBuilder import ParcelRequestBuilder as builder
client = TestClient(app)

headers = builder.build_headers(AUTH_HEADER)
def test_find_unit_by_cmd_http_resp_200():
    response = client.get("/unit/find_unit_by_cmd", headers=headers,params={"cms":"801"})
    assert response.status_code == status.HTTP_200_OK
    assert "unitName" in response.json()["body"]

def test_find_unit_by_cmd_empty_resp_20002():
    response = client.get("/unit/find_unit_by_cmd", headers=headers,params={"cms":"8014"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["header"]["resultCode"] == ErrorCodes.NO_UNIT_FOUND.code

def test_find_unit_by_cmd_auth_resp_422():
    response = client.get("/unit/find_unit_by_cmd", headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY