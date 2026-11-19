"""
TruthLens - REST API Endpoints Integration Test
Tests FastAPI endpoints for health, sample cases, ingestion, and report generation.
"""

import pytest
from starlette.testclient import TestClient
from web.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "image" in data["supported_modalities"]


def test_api_sample_cases(client):
    response = client.get("/api/sample-cases")
    assert response.status_code == 200
    data = response.json()
    assert "case_deepfake_attack" in data
    assert "case_spliced_photo" in data
    assert "case_authentic_baseline" in data


def test_api_analyze_sample_case(client):
    response = client.post("/api/analyze-sample/case_deepfake_attack")
    assert response.status_code == 200
    report = response.json()
    assert "report_id" in report
    assert "assessment" in report
    assert report["assessment"]["overall_manipulation_score"] > 60.0

    report_id = report["report_id"]
    # Test report retrieval endpoints
    res_json = client.get(f"/api/reports/{report_id}")
    assert res_json.status_code == 200

    res_html = client.get(f"/api/reports/{report_id}/html")
    assert res_html.status_code == 200
    assert "TruthLens Forensic Dossier" in res_html.text

    res_md = client.get(f"/api/reports/{report_id}/markdown")
    assert res_md.status_code == 200
    assert "# Forensic Examination Report" in res_md.text


def test_api_list_cases(client):
    response = client.get("/api/cases")
    assert response.status_code == 200
    cases = response.json()
    assert isinstance(cases, list)
    assert len(cases) > 0


def test_ui_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "TruthLens" in response.text
