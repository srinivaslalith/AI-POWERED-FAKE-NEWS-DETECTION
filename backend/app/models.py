"""Pydantic models for API request/response schemas."""

from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any


class TextPredictionRequest(BaseModel):
    """Request model for text-based prediction."""
    text: str = Field(..., min_length=10, max_length=50000, description="Article text to analyze")


class URLPredictionRequest(BaseModel):
    """Request model for URL-based prediction."""
    url: HttpUrl = Field(..., description="URL of article to analyze")


class FactCheckResult(BaseModel):
    """Model for fact-check results."""
    claim: str = Field(..., description="The claim being fact-checked")
    url: str = Field(..., description="URL to the fact-check article")
    verdict: str = Field(..., description="Fact-check verdict")
    publisher: str = Field(..., description="Publisher of the fact-check")
    review_date: str = Field(default="", description="Date of the review")
    mock: Optional[bool] = Field(default=False, description="Whether this is a mock result")


class SentenceHighlight(BaseModel):
    """Model for sentence-level highlights."""
    sentence: str = Field(..., description="The sentence text")
    suspicion_score: float = Field(..., ge=0.0, le=1.0, description="Suspicion score (0-1)")
    position: int = Field(..., ge=0, description="Position in original text")
    label: str = Field(..., description="Predicted label for this sentence")


class CredibilityBreakdown(BaseModel):
    """Model for credibility score breakdown."""
    model_score: float = Field(..., description="Score from AI model (0-100)")
    factcheck_score: float = Field(..., description="Score from fact-checking (0-100)")
    source_score: float = Field(..., description="Score from source reputation (0-100)")


class ExplainabilityInfo(BaseModel):
    """Model for explainability information."""
    method: str = Field(..., description="Method used for explainability")
    details: str = Field(..., description="Details about the analysis")


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    label: str = Field(..., description="Predicted label (Fake, Real, Biased, Satire)")
    model_confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    credibility_score: float = Field(..., ge=0.0, le=100.0, description="Overall credibility score (0-100)")
    source: Optional[str] = Field(default=None, description="Source domain")
    source_reputation: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Source reputation score")
    fact_check: List[FactCheckResult] = Field(default=[], description="Fact-check results")
    highlights: List[SentenceHighlight] = Field(default=[], description="Sentence-level highlights")
    explainability: ExplainabilityInfo = Field(..., description="Explainability information")
    breakdown: CredibilityBreakdown = Field(..., description="Score breakdown")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    code: Optional[str] = Field(default=None, description="Error code")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    model_info: Dict[str, str] = Field(..., description="Model information")
    factcheck_status: Dict[str, Any] = Field(..., description="Fact-check service status")
    version: str = Field(default="1.0.0", description="API version")