"""
OCR and text parsing - Phase 2.

Handles parsing of typed/structured input into validated health answers.
Image OCR parsing will be added in Phase 3.
"""

from typing import Dict, Any, Optional, Tuple
from app.schemas import ParsedAnswers
from app.config import REQUIRED_FIELDS


class InputParser:
    """
    Parses and validates health profile input.
    
    Responsibilities:
    - Extract answers from input dict
    - Identify missing fields
    - Calculate confidence score
    - Validate field values (type, allowed values)
    """
    
    def __init__(self):
        self.required_fields = REQUIRED_FIELDS
        self.valid_exercise = {"never", "rarely", "moderate", "regular"}
        self.valid_diet = {"poor", "good", "high sugar", "balanced"}
    
    def parse_typed_input(self, input_dict: Dict[str, Any]) -> ParsedAnswers:
        """
        Parse typed health profile input.
        
        Args:
            input_dict: Raw input dictionary with possible None/missing values
        
        Returns:
            ParsedAnswers with extracted answers, missing_fields, and confidence
        
        Raises:
            ValueError: If input validation fails
        """
        # Extract non-None values from input
        answers = {}
        raw_input = {}
        
        for key, value in input_dict.items():
            if key in self.required_fields and value is not None:
                raw_input[key] = value
        
        # Validate and normalize each field
        validated_answers = self._validate_and_normalize(raw_input)
        
        # Determine missing fields
        missing = self._find_missing_fields(validated_answers)
        
        # Calculate confidence (fraction of required fields present)
        confidence = self._calculate_confidence(validated_answers)
        
        return ParsedAnswers(
            answers=validated_answers,
            missing_fields=missing,
            confidence=confidence
        )
    
    def _validate_and_normalize(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize field values.
        
        Args:
            raw_input: Extracted input with only non-None required fields
        
        Returns:
            Dictionary with validated, normalized answers
        
        Raises:
            ValueError: If validation fails
        """
        validated = {}
        
        # Validate age
        if "age" in raw_input:
            try:
                age = int(raw_input["age"])
                if age < 18 or age > 120:
                    raise ValueError(f"age must be between 18 and 120, got {age}")
                validated["age"] = age
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid age value: {str(e)}")
        
        # Validate smoker (boolean)
        if "smoker" in raw_input:
            smoker = raw_input["smoker"]
            if not isinstance(smoker, bool):
                raise ValueError(f"smoker must be boolean, got {type(smoker).__name__}")
            validated["smoker"] = smoker
        
        # Validate exercise (must be in allowed set)
        if "exercise" in raw_input:
            exercise = str(raw_input["exercise"]).lower().strip()
            if exercise not in self.valid_exercise:
                raise ValueError(
                    f"exercise must be one of {self.valid_exercise}, got '{exercise}'"
                )
            validated["exercise"] = exercise
        
        # Validate diet (must be in allowed set)
        if "diet" in raw_input:
            diet = str(raw_input["diet"]).lower().strip()
            if diet not in self.valid_diet:
                raise ValueError(
                    f"diet must be one of {self.valid_diet}, got '{diet}'"
                )
            validated["diet"] = diet
        
        return validated
    
    def _find_missing_fields(self, validated_answers: Dict[str, Any]) -> list:
        """
        Find fields that are missing from the input.
        
        Args:
            validated_answers: Dictionary of validated answers
        
        Returns:
            List of missing field names
        """
        return sorted(list(self.required_fields - set(validated_answers.keys())))
    
    def _calculate_confidence(self, validated_answers: Dict[str, Any]) -> float:
        """
        Calculate confidence score as fraction of required fields present.
        
        Args:
            validated_answers: Dictionary of validated answers
        
        Returns:
            Confidence score from 0.0 to 1.0
        """
        present_count = len(validated_answers)
        total_required = len(self.required_fields)
        
        if total_required == 0:
            return 1.0
        
        return present_count / total_required
