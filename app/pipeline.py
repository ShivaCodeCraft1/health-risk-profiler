"""
Pipeline orchestrator - chains OCR, parsing, validation, and risk assessment.

PHASE 1: Placeholder only. Full implementation in Phase 8.
"""

from typing import Dict, Any
from app.schemas import CompleteProfileAssessment


class ProfilePipeline:
    """
    Orchestrates the full health risk assessment pipeline.
    
    Pipeline stages (to be implemented in phases 2-7):
    1. Parse/OCR input
    2. Validate answers (check guardrail for >50% missing)
    3. Extract risk factors
    4. Classify risk level and score
    5. Generate recommendations
    """
    
    async def process_typed_input(self, profile: Dict[str, Any]) -> CompleteProfileAssessment:
        """
        Process typed health profile input.
        
        PHASE 1: Placeholder - returns empty assessment.
        Will be implemented in Phase 8.
        """
        return CompleteProfileAssessment(status="ok")
    
    async def process_image_input(self, content: bytes) -> CompleteProfileAssessment:
        """
        Process scanned form image input.
        
        PHASE 1: Placeholder - returns empty assessment.
        Will be implemented in Phase 8.
        """
        return CompleteProfileAssessment(status="ok")