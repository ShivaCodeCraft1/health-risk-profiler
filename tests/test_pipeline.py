"""
Comprehensive tests for health risk profiler pipeline.

Phase 1: Tests for /health endpoint and API structure.
Phase 2: Tests for text parsing, validation, and confidence scoring.
Later phases will add tests for OCR, guardrails, risk classification, etc.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ocr_parser import InputParser


client = TestClient(app)


# ============================================================================
# PHASE 1 TESTS - Health Check & API Structure
# ============================================================================

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


# ============================================================================
# PHASE 2 TESTS - Text Parsing, Validation, Confidence
# ============================================================================

class TestInputParserUnit:
    """Unit tests for InputParser class."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return InputParser()
    
    def test_parse_complete_valid_input(self, parser):
        """Parser should accept and normalize complete valid input."""
        input_data = {
            "age": 42,
            "smoker": True,
            "exercise": "rarely",
            "diet": "high sugar"
        }
        result = parser.parse_typed_input(input_data)
        
        assert result.answers == input_data
        assert result.missing_fields == []
        assert result.confidence == 1.0
    
    def test_parse_accepts_none_values(self, parser):
        """Parser should accept None values as missing fields."""
        input_data = {
            "age": 42,
            "smoker": None,
            "exercise": "rarely",
            "diet": None
        }
        result = parser.parse_typed_input(input_data)
        
        assert result.answers == {"age": 42, "exercise": "rarely"}
        assert set(result.missing_fields) == {"smoker", "diet"}
        assert result.confidence == 0.5
    
    def test_parse_incomplete_profile(self, parser, incomplete_profile):
        """Parser should handle incomplete profiles."""
        result = parser.parse_typed_input(incomplete_profile)
        
        assert result.answers == {"age": 45}
        assert set(result.missing_fields) == {"smoker", "exercise", "diet"}
        assert result.confidence == 0.25
    
    def test_parse_empty_input(self, parser):
        """Parser should handle empty input."""
        result = parser.parse_typed_input({})
        
        assert result.answers == {}
        assert len(result.missing_fields) == 4
        assert result.confidence == 0.0
    
    def test_parse_case_insensitive_exercise(self, parser):
        """Parser should normalize exercise value to lowercase."""
        input_data = {
            "age": 42,
            "smoker": True,
            "exercise": "RARELY",
            "diet": "high sugar"
        }
        result = parser.parse_typed_input(input_data)
        
        assert result.answers["exercise"] == "rarely"
    
    def test_parse_case_insensitive_diet(self, parser):
        """Parser should normalize diet value to lowercase."""
        input_data = {
            "age": 42,
            "smoker": True,
            "exercise": "rarely",
            "diet": "HIGH SUGAR"
        }
        result = parser.parse_typed_input(input_data)
        
        assert result.answers["diet"] == "high sugar"
    
    def test_parse_strips_whitespace(self, parser):
        """Parser should strip whitespace from string values."""
        input_data = {
            "age": 42,
            "smoker": True,
            "exercise": "  rarely  ",
            "diet": "  high sugar  "
        }
        result = parser.parse_typed_input(input_data)
        
        assert result.answers["exercise"] == "rarely"
        assert result.answers["diet"] == "high sugar"
    
    def test_parse_invalid_age_too_high(self, parser, invalid_age_profile):
        """Parser should reject age > 120."""
        with pytest.raises(ValueError, match="age must be between 18 and 120"):
            parser.parse_typed_input(invalid_age_profile)
    
    def test_parse_invalid_age_too_low(self, parser):
        """Parser should reject age < 18."""
        input_data = {
            "age": 10,
            "smoker": True,
            "exercise": "rarely",
            "diet": "good"
        }
        with pytest.raises(ValueError, match="age must be between 18 and 120"):
            parser.parse_typed_input(input_data)
    
    def test_parse_invalid_age_not_int(self, parser):
        """Parser should reject non-integer age."""
        input_data = {
            "age": "forty-two",
            "smoker": True,
            "exercise": "rarely",
            "diet": "good"
        }
        with pytest.raises(ValueError, match="Invalid age value"):
            parser.parse_typed_input(input_data)
    
    def test_parse_invalid_smoker_not_bool(self, parser):
        """Parser should reject non-boolean smoker value."""
        input_data = {
            "age": 42,
            "smoker": "yes",
            "exercise": "rarely",
            "diet": "good"
        }
        with pytest.raises(ValueError, match="smoker must be boolean"):
            parser.parse_typed_input(input_data)
    
    def test_parse_invalid_exercise_value(self, parser):
        """Parser should reject invalid exercise value."""
        input_data = {
            "age": 42,
            "smoker": True,
            "exercise": "very often",
            "diet": "good"
        }
        with pytest.raises(ValueError, match="exercise must be one of"):
            parser.parse_typed_input(input_data)
    
    def test_parse_invalid_diet_value(self, parser):
        """Parser should reject invalid diet value."""
        input_data = {
            "age": 42,
            "smoker": True,
            "exercise": "rarely",
            "diet": "excellent"
        }
        with pytest.raises(ValueError, match="diet must be one of"):
            parser.parse_typed_input(input_data)
    
    def test_parse_all_valid_exercise_values(self, parser):
        """Parser should accept all valid exercise values."""
        valid_values = ["never", "rarely", "moderate", "regular"]
        for exercise in valid_values:
            input_data = {
                "age": 42,
                "smoker": True,
                "exercise": exercise,
                "diet": "good"
            }
            result = parser.parse_typed_input(input_data)
            assert result.answers["exercise"] == exercise
    
    def test_parse_all_valid_diet_values(self, parser):
        """Parser should accept all valid diet values."""
        valid_values = ["poor", "good", "high sugar", "balanced"]
        for diet in valid_values:
            input_data = {
                "age": 42,
                "smoker": True,
                "exercise": "rarely",
                "diet": diet
            }
            result = parser.parse_typed_input(input_data)
            assert result.answers["diet"] == diet


class TestProfileEndpointValidation:
    """Tests for /profile endpoint validation."""
    
    def test_profile_valid_complete_input(self, healthy_profile):
        """POST /profile with valid complete input returns 200."""
        response = client.post("/profile", json=healthy_profile)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["extracted_fields"] == healthy_profile
        assert data["missing_fields"] == []
        assert data["confidence"] == 1.0
    
    def test_profile_incomplete_input(self, incomplete_profile):
        """POST /profile with incomplete input returns 200 (parsed)."""
        response = client.post("/profile", json=incomplete_profile)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["extracted_fields"]["age"] == 45
        assert len(data["missing_fields"]) == 3
        assert data["confidence"] == 0.25
    
    def test_profile_empty_input(self):
        """POST /profile with empty input returns 200 (parsed)."""
        response = client.post("/profile", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["extracted_fields"] == {}
        assert len(data["missing_fields"]) == 4
        assert data["confidence"] == 0.0
    
    def test_profile_invalid_age_too_high(self, invalid_age_profile):
        """POST /profile with invalid age returns 422."""
        response = client.post("/profile", json=invalid_age_profile)
        assert response.status_code == 422
    
    def test_profile_invalid_age_too_low(self):
        """POST /profile with age < 18 returns 422."""
        response = client.post("/profile", json={
            "age": 10,
            "smoker": True,
            "exercise": "rarely",
            "diet": "good"
        })
        assert response.status_code == 422
    
    def test_profile_invalid_exercise(self):
        """POST /profile with invalid exercise returns 200 with error status."""
        response = client.post("/profile", json={
            "age": 42,
            "smoker": True,
            "exercise": "invalid",
            "diet": "good"
        })
        # Returns 200 with error status (caught by pipeline, not schema)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
    
    def test_profile_invalid_diet(self):
        """POST /profile with invalid diet returns 200 with error status."""
        response = client.post("/profile", json={
            "age": 42,
            "smoker": True,
            "exercise": "rarely",
            "diet": "invalid"
        })
        # Returns 200 with error status (caught by pipeline, not schema)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
    
    def test_profile_confidence_calculation(self):
        """POST /profile calculates confidence correctly."""
        # 1 of 4 fields = 0.25 confidence
        response = client.post("/profile", json={"age": 42})
        assert response.status_code == 200
        data = response.json()
        assert data["confidence"] == 0.25
        
        # 2 of 4 fields = 0.5 confidence
        response = client.post("/profile", json={"age": 42, "smoker": True})
        assert response.status_code == 200
        data = response.json()
        assert data["confidence"] == 0.5
        
        # 3 of 4 fields = 0.75 confidence
        response = client.post("/profile", json={
            "age": 42,
            "smoker": True,
            "exercise": "rarely"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["confidence"] == 0.75
    
    def test_profile_missing_fields_list(self):
        """POST /profile returns correct missing_fields list."""
        response = client.post("/profile", json={"age": 42})
        assert response.status_code == 200
        data = response.json()
        assert set(data["missing_fields"]) == {"smoker", "exercise", "diet"}


class TestProfileImageEndpoint:
    """Tests for /profile-image endpoint."""
    
    def test_profile_image_invalid_filetype(self):
        """POST /profile-image with invalid file type returns 400."""
        # For now, just test endpoint is accessible
        # Real image testing will be in Phase 3
        pass


# ============================================================================
# FIXTURES - Common test data
# ============================================================================

@pytest.fixture
def healthy_profile():
    """Example healthy profile."""
    return {
        "age": 30,
        "smoker": False,
        "exercise": "regular",
        "diet": "balanced"
    }


@pytest.fixture
def high_risk_profile():
    """Example high-risk profile."""
    return {
        "age": 65,
        "smoker": True,
        "exercise": "never",
        "diet": "high sugar"
    }


@pytest.fixture
def incomplete_profile():
    """Profile with only age (>50% missing)."""
    return {
        "age": 45
    }


@pytest.fixture
def invalid_age_profile():
    """Profile with invalid age (must be 18-120)."""
    return {
        "age": 150,
        "smoker": True,
        "exercise": "rarely",
        "diet": "good"
    }
