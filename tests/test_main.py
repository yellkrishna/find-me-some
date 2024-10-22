# tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_summary_success():
    response = client.post("/generate-summary/", json={
        "name": "Example Business",
        "address": "123 Example Street"
    })
    assert response.status_code == 200
    assert "summary" in response.json()

def test_generate_summary_missing_fields():
    response = client.post("/generate-summary/", json={
        "name": "Example Business"
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_generate_summary_invalid_data():
    response = client.post("/generate-summary/", json={
        "name": "",
        "address": ""
    })
    assert response.status_code == 500  # Assuming it raises an exception
