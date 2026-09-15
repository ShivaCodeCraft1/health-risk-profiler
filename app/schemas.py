"""
Pydantic schemas for health risk profiler.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class HealthProfileInput(BaseModel):
    """
    Input schema for health profile assessment.
    
    All fields are Optional to allow incomplete profiles to reach the pipeline.
    The pipeline will calculate missing_fields, confidence, and determine
    if the profile meets minimum requirements.
    """
    age: Optional[int] = Field(None, ge=18, le=120, description="Age (18-120)")
    smoker: Optional[bool] = Field(None, description="Smoking status")
    exercise: Optional[str] = Field(None, description="Exercise frequency: never, rarely, moderate, regular")
    diet: Optional[str] = Field(None, description="Diet quality: poor, good, high sugar, balanced")


class HealthCheckResponse(BaseModel):
    """Health check endpoint response."""
    status: str = Field(..., description="Service status")


class CompleteProfileAssessment(BaseModel):
    """
    Complete assessment response.
    
    Returned by /profile endpoint after processing through the full pipeline.
    """
    status: str = Field(..., description="ok, incomplete_profile, or error")
    extracted_fields: Optional[dict] = Field(default=None, description="Extracted fields")
    missing_fields: List[str] = Field(default_factory=list, description="Missing fields")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence 0-1")
    factors: List[str] = Field(default_factory=list, description="Risk factors")
    risk_level: Optional[str] = Field(default=None, description="Risk level")
    score: Optional[int] = Field(default=None, ge=0, le=100, description="Risk score 0-100")
    rationale: List[str] = Field(default_factory=list, description="Risk rationale")
    recommendations: List[str] = Field(default_factory=list, description="Health recommendations")
    reason: Optional[str] = Field(default=None, description="Reason for incomplete/error status")