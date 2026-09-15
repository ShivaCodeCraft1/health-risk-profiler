"""
Configuration and constants for the health risk profiler.
"""

# Required fields for health profile
REQUIRED_FIELDS = {"age", "smoker", "exercise", "diet"}

# Guardrail threshold: reject if more than this fraction is missing
MISSING_FIELD_THRESHOLD = 0.5  # >50% missing → incomplete_profile

# Risk scoring thresholds (score 0-100 → risk level)
RISK_THRESHOLDS = {
    "low": (0, 35),          # 0-34: low
    "moderate": (35, 60),    # 35-59: moderate
    "high": (60, 80),        # 60-79: high
    "very_high": (80, 100)   # 80-100: very_high
}

# Factor to score points mapping (used in Phase 6)
FACTOR_SCORES = {
    "smoking": 25,
    "poor diet": 20,
    "high sugar diet": 18,
    "sedentary": 20,
    "low exercise": 15,
    "age 45+": 10,
    "age 55+": 15,
    "age 65+": 20,
}

# Exercise level → risk factor mapping (used in Phase 5)
EXERCISE_RISK_MAP = {
    "never": "sedentary",
    "rarely": "low exercise",
    "moderate": None,
    "regular": None,
}

# Diet quality → risk factor mapping (used in Phase 5)
DIET_RISK_MAP = {
    "poor": "poor diet",
    "high sugar": "high sugar diet",
    "good": None,
    "balanced": None,
}

# Recommendations by factor (used in Phase 7)
RECOMMENDATIONS_MAP = {
    "smoking": [
        "Quit smoking - consult a healthcare provider for support programs",
        "Consider nicotine replacement therapy or prescription medications",
    ],
    "poor diet": [
        "Increase intake of fruits, vegetables, and whole grains",
        "Reduce processed foods and sugary drinks",
    ],
    "high sugar diet": [
        "Reduce sugar intake - replace sugary drinks with water",
        "Choose whole grains over refined carbohydrates",
    ],
    "sedentary": [
        "Start with 30 minutes of moderate exercise, 5 days per week",
        "Consider activities you enjoy: walking, swimming, cycling",
    ],
    "low exercise": [
        "Aim for at least 150 minutes of moderate exercise per week",
        "Add strength training 2-3 times per week",
    ],
    "age 45+": [
        "Regular health screenings are important",
        "Consult healthcare provider for preventive care",
    ],
    "age 55+": [
        "Schedule regular cardiovascular health checks",
        "Monitor blood pressure and cholesterol levels",
    ],
    "age 65+": [
        "Annual comprehensive health assessments recommended",
        "Stay current with vaccinations and preventive care",
    ],
}

# OCR configuration (used in Phase 3)
OCR_CONFIG = {
    "timeout": 30,  # seconds
}