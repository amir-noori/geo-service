import pytest
from fastapi.testclient import TestClient
from geoservice.app import app
from integration.test_apis.RequestBuilder import ParcelRequestBuilder
client = TestClient(app)

def test_find_state_polygon():
    params = {
        "state_code": "8"
    }
    headers = ParcelRequestBuilder.build_headers("100:123")
    response = client.get("/parcels/find_state_polygon",headers=headers ,params=params)
    assert response.status_code == 200
    assert "geom" in response.json()["body"]  
