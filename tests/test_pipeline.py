"""
Comprehensive tests for health risk profiler pipeline.

Phase 1: Tests for /health endpoint and API structure.
Later phases will add tests for parsing, OCR, validation, etc.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestHealthCheck:
    """Tests for /health endpoint."""
    
    def test_health_check_returns_ok(self):
        """GET /health should return status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestRootEndpoint:
    """Tests for / endpoint."""
    
    def test_root_returns_api_info(self):
        """GET / should return API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "endpoints" in data


class TestSwaggerDocumentation:
    """Tests for API documentation endpoints."""
    
    def test_swagger_docs_available(self):
        """GET /docs should return Swagger UI."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()
    
    def test_redoc_docs_available(self):
        """GET /redoc should return ReDoc UI."""
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_openapi_schema_available(self):
        """GET /openapi.json should return OpenAPI schema."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema
        assert "info" in schema


class TestProfileEndpoints:
    """Tests for /profile and /profile-image endpoints (Phase 1 placeholders)."""
    
    def test_profile_endpoint_exists(self):
        """POST /profile should be available."""
        response = client.post("/profile", json={})
        # Phase 1: Just ensure endpoint exists and responds
        assert response.status_code in [200, 422]  # May be validation error
    
    def test_profile_image_endpoint_exists(self):
        """POST /profile-image should be available."""
        # Will test with actual image in Phase 3
        pass


class TestValidation:
    """Tests for input validation (Phase 1)."""
    
    def test_invalid_age_too_high(self, invalid_age_profile):
        """Age > 120 should fail validation."""
        response = client.post("/profile", json=invalid_age_profile)
        # Pydantic should reject age=150
        assert response.status_code == 422
    
    def test_invalid_age_too_low(self):
        """Age < 18 should fail validation."""
        response = client.post("/profile", json={
            "age": 10,
            "smoker": True,
            "exercise": "rarely",
            "diet": "good"
        })
        assert response.status_code == 422
    
    def test_incomplete_profile_accepted(self, incomplete_profile):
        """Incomplete profile should reach pipeline (not rejected by schema)."""
        response = client.post("/profile", json=incomplete_profile)
        # Schema accepts incomplete profile; pipeline will handle it
        assert response.status_code == 200