import os
import pytest
from fastapi.testclient import TestClient
from geoservice.app import app  # Import the app from your app.py

@pytest.fixture(scope="module")
def client():
    """
    Creates a TestClient for FastAPI app, used to simulate HTTP requests during testing.
    """    
    with TestClient(app) as test_client:
        yield test_client
