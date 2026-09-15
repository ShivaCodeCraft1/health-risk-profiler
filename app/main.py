"""
Main FastAPI application entry point.

This is Phase 1 - skeleton only. The /profile endpoint will be fully
implemented in Phase 8 after all components are built.
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.schemas import HealthCheckResponse, CompleteProfileAssessment, HealthProfileInput
from app.pipeline import ProfilePipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Health Risk Profiler",
    description="Analyzes health survey responses and generates risk assessments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = ProfilePipeline()


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint to verify service is running.
    
    **Returns:**
    - `status`: "ok" if service is healthy
    """
    return HealthCheckResponse(status="ok")


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "AI-Powered Health Risk Profiler API",
        "version": "1.0.0",
        "docs": "/docs",
        "health_check": "/health",
        "endpoints": {
            "POST /profile": "Assess health profile from typed input",
            "POST /profile-image": "Assess health profile from scanned image",
        }
    }


@app.post("/profile", response_model=CompleteProfileAssessment)
async def assess_profile(profile: HealthProfileInput):
    """
    Complete health risk assessment from typed input.
    
    Processes a health profile through the full pipeline:
    1. Parse/validate answers
    2. Check guardrail (>50% missing → reject)
    3. Extract risk factors
    4. Classify risk level and score
    5. Generate personalized recommendations
    
    **Example request:**
    ```json
    {
      "age": 42,
      "smoker": true,
      "exercise": "rarely",
      "diet": "high sugar"
    }
    ```
    
    **Example response (moderate-risk profile):**
    ```json
    {
      "status": "ok",
      "extracted_fields": {"age": 42, "smoker": true, "exercise": "rarely", "diet": "high sugar"},
      "missing_fields": [],
      "confidence": 1.0,
      "factors": ["smoking", "high sugar diet", "low exercise"],
      "risk_level": "moderate",
      "score": 58,
      "rationale": ["smoking", "high sugar diet", "low activity"],
      "recommendations": ["Quit smoking", "Reduce sugar", "Walk 30 mins daily"],
      "reason": null
    }
    ```
    
    **Incomplete profile response:**
    ```json
    {
      "status": "incomplete_profile",
      "extracted_fields": {"age": 42},
      "missing_fields": ["smoker", "exercise", "diet"],
      "confidence": 0.25,
      "reason": ">50% fields missing"
    }
    ```
    """
    try:
        result = await pipeline.process_typed_input(profile.dict(exclude_none=False))
        return result
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/profile-image", response_model=CompleteProfileAssessment)
async def assess_profile_from_image(file: UploadFile = File(...)):
    """
    Complete health risk assessment from scanned form image.
    
    Accepts a JPG or PNG image containing a health survey form.
    
    Pipeline:
    1. Extract text from image (OCR)
    2. Parse answers from extracted text
    3. Check guardrail
    4. Extract risk factors
    5. Classify risk level and score
    6. Generate recommendations
    
    Supports noisy/imperfect OCR output.
    
    **Supported file types:** JPEG, PNG
    """
    try:
        # Validate file type
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=400,
                detail="File must be JPG or PNG image"
            )
        
        # Read file
        content = await file.read()
        
        result = await pipeline.process_image_input(content)
        return result
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)