"""Main FastAPI application for the fake news detector."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

from .models import (
    TextPredictionRequest, URLPredictionRequest, PredictionResponse,
    ErrorResponse, HealthResponse
)
from .config import config
try:
    from .nlp_engine import FakeNewsDetector
except ImportError as e:
    logger.warning(f"Could not import full NLP engine ({e}), using mock version")
    from .nlp_engine_mock import FakeNewsDetector
from .factcheck_adapter import FactCheckAdapter
from .scoring import CredibilityScorer
from .scraper import ArticleScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Global instances
nlp_detector = None
fact_checker = None
scorer = None
scraper = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    global nlp_detector, fact_checker, scorer, scraper
    
    # Startup
    logger.info("Starting Fake News Detector API...")
    
    try:
        # Initialize components
        logger.info("Initializing NLP detector...")
        nlp_detector = FakeNewsDetector(
            model_name=config.model_name,
            max_length=config.model_max_length
        )
        
        logger.info("Initializing fact-checker...")
        fact_checker = FactCheckAdapter(api_key=config.factcheck_api_key)
        
        logger.info("Initializing scorer...")
        scorer = CredibilityScorer(
            weights=config.scoring_weights,
            domain_reputation_file=config.domain_reputation_file
        )
        
        logger.info("Initializing scraper...")
        scraper = ArticleScraper()
        
        logger.info("All components initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Fake News Detector API...")


# Create FastAPI app
app = FastAPI(
    title="AI-Powered Fake News Detector",
    description="Detect fake news using AI models, fact-checking, and source reputation analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)}
    )


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "AI-Powered Fake News Detector API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        model_info = nlp_detector.get_model_info() if nlp_detector else {}
        factcheck_status = fact_checker.get_status() if fact_checker else {}
        
        return HealthResponse(
            status="healthy",
            model_info=model_info,
            factcheck_status=factcheck_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )


@app.post("/predict", response_model=PredictionResponse)
async def predict_text(request: TextPredictionRequest):
    """Predict credibility of article text."""
    try:
        # Get model prediction
        logger.info(f"Analyzing text of length {len(request.text)}")
        model_prediction = nlp_detector.predict(request.text)
        
        # Get sentence-level analysis
        sentence_analysis = nlp_detector.analyze_sentences(request.text)
        
        # Get fact-check results
        fact_check_results = fact_checker.check_claims(request.text)
        
        # Calculate credibility score
        scoring_result = scorer.calculate_credibility_score(
            model_prediction=model_prediction,
            fact_check_results=fact_check_results,
            domain=None  # No domain for direct text input
        )
        
        # Prepare highlights (top 5 most suspicious sentences)
        highlights = [
            {
                "sentence": item["sentence"],
                "suspicion_score": item["suspicion_score"],
                "position": item["position"],
                "label": item["label"]
            }
            for item in sentence_analysis[:5]
        ]
        
        return PredictionResponse(
            label=model_prediction["label"],
            model_confidence=model_prediction["confidence"],
            credibility_score=scoring_result["credibility_score"],
            source=None,
            source_reputation=None,
            fact_check=fact_check_results,
            highlights=highlights,
            explainability={
                "method": "sentence_scoring",
                "details": f"Analyzed {len(sentence_analysis)} sentences using {nlp_detector.model_name}"
            },
            breakdown=scoring_result["breakdown"],
            metadata={
                "text_length": len(request.text),
                "sentences_analyzed": len(sentence_analysis),
                "model_truncated": model_prediction.get("truncated", False)
            }
        )
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/predict-url", response_model=PredictionResponse)
async def predict_url(request: URLPredictionRequest):
    """Predict credibility of article from URL."""
    try:
        # Scrape article content
        logger.info(f"Scraping article from URL: {request.url}")
        scrape_result = scraper.extract_article(str(request.url))
        
        if scrape_result["error"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to scrape article: {scrape_result['error']}"
            )
        
        if not scrape_result["text"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No article content found at the provided URL"
            )
        
        # Get model prediction
        model_prediction = nlp_detector.predict(scrape_result["text"])
        
        # Get sentence-level analysis
        sentence_analysis = nlp_detector.analyze_sentences(scrape_result["text"])
        
        # Get fact-check results
        fact_check_results = fact_checker.check_claims(scrape_result["text"])
        
        # Calculate credibility score
        scoring_result = scorer.calculate_credibility_score(
            model_prediction=model_prediction,
            fact_check_results=fact_check_results,
            domain=scrape_result["domain"]
        )
        
        # Prepare highlights (top 5 most suspicious sentences)
        highlights = [
            {
                "sentence": item["sentence"],
                "suspicion_score": item["suspicion_score"],
                "position": item["position"],
                "label": item["label"]
            }
            for item in sentence_analysis[:5]
        ]
        
        return PredictionResponse(
            label=model_prediction["label"],
            model_confidence=model_prediction["confidence"],
            credibility_score=scoring_result["credibility_score"],
            source=scrape_result["domain"],
            source_reputation=scoring_result["source_reputation"],
            fact_check=fact_check_results,
            highlights=highlights,
            explainability={
                "method": "sentence_scoring",
                "details": f"Analyzed {len(sentence_analysis)} sentences using {nlp_detector.model_name}"
            },
            breakdown=scoring_result["breakdown"],
            metadata={
                "url": str(request.url),
                "title": scrape_result["title"],
                "text_length": len(scrape_result["text"]),
                "sentences_analyzed": len(sentence_analysis),
                "model_truncated": model_prediction.get("truncated", False)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"URL prediction failed: {str(e)}"
        )


@app.get("/config", response_model=Dict[str, Any])
async def get_config():
    """Get current configuration and scoring explanation."""
    try:
        return {
            "model": {
                "name": config.model_name,
                "max_length": config.model_max_length
            },
            "factcheck": {
                "enabled": config.factcheck_enabled,
                "service": "Google Fact Check Tools API" if config.factcheck_enabled else "Mock service"
            },
            "scoring": scorer.get_scoring_explanation() if scorer else {},
            "domain_reputation_count": len(scorer.domain_reputation) if scorer else 0
        }
    except Exception as e:
        logger.error(f"Config retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve configuration"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.get("app.host", "0.0.0.0"),
        port=config.get("app.port", 8000),
        reload=config.get("app.debug", True)
    )