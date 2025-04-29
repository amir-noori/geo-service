import os
import pytest
from fastapi.testclient import TestClient
from geoservice.app import app

@pytest.fixture(scope="module")
def createTestClient():
    """
    Creates a TestClient for FastAPI app, used to simulate HTTP requests during testing.
    """    
    with TestClient(app) as test_client:
        yield test_client
