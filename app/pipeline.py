"""
Pipeline orchestrator - chains parsing, validation, and risk assessment.

Phase 2: Implements text parsing stage.
Phases 3-8: Will add OCR, guardrails, factor extraction, risk, recommendations.
"""

from typing import Dict, Any
from app.schemas import CompleteProfileAssessment
from app.ocr_parser import InputParser


class ProfilePipeline:
    """
    Orchestrates the full health risk assessment pipeline.
    
    Pipeline stages:
    1. Parse/OCR input ✅ (Phase 2)
    2. Check guardrail for >50% missing (Phase 4)
    3. Extract risk factors (Phase 5)
    4. Classify risk level and score (Phase 6)
    5. Generate recommendations (Phase 7)
    """
    
    def __init__(self):
        self.parser = InputParser()
    
    async def process_typed_input(self, profile: Dict[str, Any]) -> CompleteProfileAssessment:
        """
        Process typed health profile input through the pipeline.
        
        Phase 2: Parses and validates input, returns parsed answers with confidence.
        Future phases will add guardrails, factor extraction, risk classification, recommendations.
        
        Args:
            profile: Dictionary with optional fields (age, smoker, exercise, diet)
        
        Returns:
            CompleteProfileAssessment with parsed data
        """
        try:
            # Phase 2: Parse and validate typed input
            parsed = self.parser.parse_typed_input(profile)
            
            # Phase 2: Return parsed result (future phases will continue pipeline)
            return CompleteProfileAssessment(
                status="ok",
                extracted_fields=parsed.answers,
                missing_fields=parsed.missing_fields,
                confidence=parsed.confidence,
                factors=[],
                risk_level=None,
                score=None,
                rationale=[],
                recommendations=[],
                reason=None
            )
        
        except ValueError as e:
            # Validation error - return as error status
            return CompleteProfileAssessment(
                status="error",
                extracted_fields=None,
                missing_fields=[],
                confidence=None,
                factors=[],
                risk_level=None,
                score=None,
                rationale=[],
                recommendations=[],
                reason=str(e)
            )
        
        except Exception as e:
            # Unexpected error
            return CompleteProfileAssessment(
                status="error",
                extracted_fields=None,
                missing_fields=[],
                confidence=None,
                factors=[],
                risk_level=None,
                score=None,
                rationale=[],
                recommendations=[],
                reason=f"Unexpected error: {str(e)}"
            )
    
    async def process_image_input(self, content: bytes) -> CompleteProfileAssessment:
        """
        Process scanned form image input.
        
        Phase 3: Will implement OCR extraction.
        Phase 2: Placeholder - returns error.
        
        Args:
            content: Image file content (bytes)
        
        Returns:
            CompleteProfileAssessment (error status until Phase 3)
        """
        return CompleteProfileAssessment(
            status="error",
            extracted_fields=None,
            missing_fields=[],
            confidence=None,
            factors=[],
            risk_level=None,
            score=None,
            rationale=[],
            recommendations=[],
            reason="Image processing not yet implemented (Phase 3)"
        )
