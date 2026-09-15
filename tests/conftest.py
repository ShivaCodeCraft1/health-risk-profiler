"""
Pytest configuration and fixtures.
"""

import pytest


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