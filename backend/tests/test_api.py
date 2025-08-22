"""Unit tests for the fake news detector API."""

import pytest
from fastapi.testclient import TestClient
import json
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app

client = TestClient(app)


class TestAPI:
    """Test cases for the API endpoints."""
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "model_info" in data
        assert "factcheck_status" in data
    
    def test_config_endpoint(self):
        """Test the configuration endpoint."""
        response = client.get("/config")
        assert response.status_code == 200
        data = response.json()
        assert "model" in data
        assert "factcheck" in data
        assert "scoring" in data
    
    def test_predict_text_valid(self):
        """Test text prediction with valid input."""
        payload = {
            "text": "Breaking: Scientists discover miracle cure that reverses aging overnight — details inside."
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "label" in data
        assert "model_confidence" in data
        assert "credibility_score" in data
        assert "highlights" in data
        assert "explainability" in data
        assert "breakdown" in data
        
        # Validate score ranges
        assert 0 <= data["credibility_score"] <= 100
        assert 0 <= data["model_confidence"] <= 1
    
    def test_predict_text_short(self):
        """Test text prediction with text that's too short."""
        payload = {"text": "Short"}
        response = client.post("/predict", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_predict_text_empty(self):
        """Test text prediction with empty text."""
        payload = {"text": ""}
        response = client.post("/predict", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_predict_url_invalid(self):
        """Test URL prediction with invalid URL."""
        payload = {"url": "not-a-valid-url"}
        response = client.post("/predict-url", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_predict_url_valid_format(self):
        """Test URL prediction with valid URL format."""
        # Note: This might fail in actual scraping, but should pass validation
        payload = {"url": "https://example.com/article"}
        response = client.post("/predict-url", json=payload)
        # Could be 200 (success) or 400 (scraping failed)
        assert response.status_code in [200, 400]


def test_sample_fake_news():
    """Test with a sample fake news text."""
    fake_text = """
    BREAKING: Government secretly adds mind control chemicals to tap water, 
    scientists confirm 99% of population affected. Local doctor reveals shocking 
    truth that mainstream media doesn't want you to know. Click here for the 
    real story they're trying to hide from you.
    """
    
    payload = {"text": fake_text}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    # Should detect this as suspicious
    assert data["credibility_score"] < 50  # Low credibility expected


def test_sample_real_news():
    """Test with a sample real news text."""
    real_text = """
    The Federal Reserve announced today that it will maintain interest rates 
    at their current level following the conclusion of their two-day policy meeting. 
    Fed Chair Jerome Powell cited ongoing economic uncertainty and inflation concerns 
    as key factors in the decision. The central bank's statement indicated that 
    future rate decisions will depend on incoming economic data and inflation trends.
    """
    
    payload = {"text": real_text}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    # Should be more credible than fake news
    assert isinstance(data["credibility_score"], (int, float))
    assert 0 <= data["credibility_score"] <= 100


if __name__ == "__main__":
    pytest.main([__file__])