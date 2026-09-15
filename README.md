# AI-Powered Health Risk Profiler

Internship assignment: Build a service that accepts health survey responses (typed or scanned) and generates risk assessments with personalized recommendations.

## Problem Statement

Develop a service that analyzes lifestyle survey responses and generates a structured health risk profile with factors, risk level, and actionable recommendations. The system must handle:

- **Typed input:** Structured JSON health survey
- **Image input:** Scanned/photographed survey forms
- **Noisy data:** OCR errors, missing fields, invalid values
- **Incomplete profiles:** Reject if >50% of fields are missing
- **Risk assessment:** Deterministic scoring (non-diagnostic, educational only)
- **Recommendations:** Personalized health guidance

## Architecture

```
User Input (Text or Image)
    ↓
Phase 2: Parse / OCR
    ↓
Phase 4: Guardrail (>50% missing check)
    ├─ Reject? → Return incomplete_profile
    └─ Continue
    ↓
Phase 5: Extract Factors
    ↓
Phase 6: Classify Risk
    ↓
Phase 7: Generate Recommendations
    ↓
Final JSON Response
```

## Tech Stack

- **Framework:** FastAPI (0.115+)
- **Validation:** Pydantic (2.7+)
- **OCR:** pytesseract + Tesseract (Phase 3)
- **Image Processing:** Pillow (10.2+)
- **Testing:** pytest (8.0+)
- **Server:** uvicorn (0.30+)

## Project Structure

```
health-risk-profiler/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── schemas.py              # Pydantic models
│   ├── config.py               # Constants and configuration
│   ├── pipeline.py             # Orchestrator (phases 2-8)
│   ├── ocr_parser.py           # OCR and text parsing (phase 3)
│   ├── factor_extraction.py    # Answer → factors (phase 5)
│   ├── risk_classifier.py      # Risk scoring (phase 6)
│   └── recommendations.py      # Recommendations (phase 7)
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   └── test_pipeline.py        # All tests
├── sample_requests/            # Example input files
├── requirements.txt
├── README.md
├── .gitignore
└── .env.example
```

## Installation

### Prerequisites

- Python 3.9+
- pip
- Tesseract OCR (for image input)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ShivaCodeCraft1/health-risk-profiler.git
   cd health-risk-profiler
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR (if needed for image input):**
   
   **macOS:**
   ```bash
   brew install tesseract
   ```
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get install tesseract-ocr
   ```
   
   **Windows:**
   - Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
   - Run installer
   - Note installation path (e.g., `C:\Program Files\Tesseract-OCR`)

5. **Environment variables (optional):**
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

## Running the Application

### Start the server:

```bash
uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000`

### API Documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

## Testing

```bash
pytest tests/ -v
```

Run specific test class:
```bash
pytest tests/test_pipeline.py::TestHealthCheck -v
```

## API Endpoints

### Health Check
```bash
GET /health
```

**Response:**
```json
{"status": "ok"}
```

---

### Assess Profile (Typed Input)
```bash
POST /profile
Content-Type: application/json

{
  "age": 42,
  "smoker": true,
  "exercise": "rarely",
  "diet": "high sugar"
}
```

**Response (Moderate Risk):**
```json
{
  "status": "ok",
  "extracted_fields": {
    "age": 42,
    "smoker": true,
    "exercise": "rarely",
    "diet": "high sugar"
  },
  "missing_fields": [],
  "confidence": 1.0,
  "factors": ["smoking", "high sugar diet", "low exercise"],
  "risk_level": "moderate",
  "score": 58,
  "rationale": ["smoking", "high sugar diet", "low activity"],
  "recommendations": [
    "Quit smoking - consult a healthcare provider for support programs",
    "Reduce sugar intake - replace sugary drinks with water or herbal tea",
    "Start with 30 minutes of moderate exercise, 5 days per week"
  ],
  "reason": null
}
```

**Response (Incomplete Profile):**
```json
{
  "status": "incomplete_profile",
  "extracted_fields": {"age": 42},
  "missing_fields": ["smoker", "exercise", "diet"],
  "confidence": 0.25,
  "factors": [],
  "risk_level": null,
  "score": null,
  "rationale": [],
  "recommendations": [],
  "reason": ">50% fields missing"
}
```

---

### Assess Profile (Image Input)
```bash
POST /profile-image
Content-Type: multipart/form-data

file: <image.jpg or image.png>
```

Supports JPG and PNG images of scanned survey forms. Handles OCR noise and imperfections.

---

## Example Usage

### cURL - Typed Input:
```bash
curl -X POST http://localhost:8000/profile \
  -H "Content-Type: application/json" \
  -d '{
    "age": 42,
    "smoker": true,
    "exercise": "rarely",
    "diet": "high sugar"
  }'
```

### cURL - Image Input:
```bash
curl -X POST http://localhost:8000/profile-image \
  -F "file=@sample_form.png"
```

### Python Requests:
```python
import requests

profile = {
    "age": 42,
    "smoker": True,
    "exercise": "rarely",
    "diet": "high sugar"
}

response = requests.post("http://localhost:8000/profile", json=profile)
print(response.json())
```

## Risk Scoring

The risk score (0-100) is calculated deterministically based on identified health factors:

| Score Range | Risk Level |
|------------|------------|
| 0-34 | Low |
| 35-59 | Moderate |
| 60-79 | High |
| 80-100 | Very High |

**Score Calculation:**
- Each risk factor contributes a fixed number of points (see `app/config.py`)
- Example: smoking (+25) + high sugar diet (+18) + low exercise (+15) = 58 (Moderate)

**Guardrail:**
- If >50% of fields are missing, profile is rejected as "incomplete_profile"
- Confidence = (fields present) / (required fields)

## Expected Inputs

### Valid Fields:

- **age:** Integer, 18-120
- **smoker:** Boolean (true/false)
- **exercise:** String from [never, rarely, moderate, regular]
- **diet:** String from [poor, good, high sugar, balanced]

### Incomplete Profile:
If any field is missing, it is tracked. If >50% missing → incomplete_profile status.

### Invalid Input:
- age outside 18-120 → 422 Unprocessable Entity
- exercise not in allowed values → 422
- diet not in allowed values → 422

## Sample Data

Included in `sample_requests/`:
- `text_input.json` — Standard profile
- `high_risk.json` — High-risk profile
- `incomplete.json` — Missing >50% fields
- `invalid.json` — Invalid age (150)

Use these to test:
```bash
curl -X POST http://localhost:8000/profile \
  -H "Content-Type: application/json" \
  -d @sample_requests/text_input.json
```

## Risk Scoring Policy

**This is a non-diagnostic, educational heuristic created for this assignment.**

The scoring is based on:
1. Presence of major risk factors (smoking, diet quality, exercise)
2. Age-based risk escalation (45+, 55+, 65+)
3. Factor interactions (e.g., smoker + sedentary = higher risk)

**Important:** This assessment is for educational purposes only and does not replace professional medical advice. Always consult a qualified healthcare provider for medical concerns.

## Limitations

- **Non-Medical:** This tool is educational and does not provide medical diagnosis
- **Synthetic Logic:** Risk scoring uses heuristic logic, not validated medical models
- **Input Quality:** OCR quality depends on image clarity and handwriting legibility
- **Incomplete Profiles:** Cannot generate risk assessment with >50% missing fields

## Disclaimer

**This application is not a medical device and should NOT be used for medical diagnosis or treatment decisions.**

- The risk scores and recommendations are educational only
- Results do not constitute medical advice
- Always consult qualified healthcare professionals for medical concerns
- In case of medical emergency, contact emergency services

## Development Status

✅ Phase 1: FastAPI skeleton + health endpoint
⏳ Phase 2: Text parsing
⏳ Phase 3: Image OCR
⏳ Phase 4: Guardrails
⏳ Phase 5: Factor extraction
⏳ Phase 6: Risk classification
⏳ Phase 7: Recommendations
⏳ Phase 8: Full pipeline

## Contributing

This is an assignment project. For changes, create a feature branch and submit a pull request.

## License

MIT License

## Author

Built as an internship assignment demonstrating backend engineering, AI integration, and validation practices.