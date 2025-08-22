#!/usr/bin/env python3
"""
Demo script for testing the Fake News Detector components.
Run this to verify the backend modules work correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.config import config
from backend.app.nlp_engine import FakeNewsDetector
from backend.app.factcheck_adapter import FactCheckAdapter
from backend.app.scoring import CredibilityScorer
from backend.app.scraper import ArticleScraper

def test_components():
    """Test all components individually."""
    print("🔍 Testing Fake News Detector Components")
    print("=" * 50)
    
    # Test 1: Configuration
    print("\n1. Testing Configuration...")
    print(f"   Model: {config.model_name}")
    print(f"   Max Length: {config.model_max_length}")
    print(f"   Fact-check enabled: {config.factcheck_enabled}")
    print(f"   Scoring weights: {config.scoring_weights}")
    
    # Test 2: NLP Engine
    print("\n2. Testing NLP Engine...")
    try:
        detector = FakeNewsDetector(config.model_name, config.model_max_length)
        
        fake_text = "Breaking: Scientists discover miracle cure that reverses aging overnight!"
        real_text = "The Federal Reserve announced interest rate decisions today."
        
        fake_result = detector.predict(fake_text)
        real_result = detector.predict(real_text)
        
        print(f"   Fake news prediction: {fake_result['label']} (confidence: {fake_result['confidence']:.2f})")
        print(f"   Real news prediction: {real_result['label']} (confidence: {real_result['confidence']:.2f})")
        
    except Exception as e:
        print(f"   ❌ NLP Engine failed: {e}")
        return False
    
    # Test 3: Fact Checker
    print("\n3. Testing Fact Checker...")
    fact_checker = FactCheckAdapter(config.factcheck_api_key)
    fact_results = fact_checker.check_claims("Test claim for fact checking")
    print(f"   Fact-check results: {len(fact_results)} claims")
    if fact_results:
        print(f"   First result: {fact_results[0]['verdict']}")
    
    # Test 4: Scoring
    print("\n4. Testing Credibility Scorer...")
    scorer = CredibilityScorer(config.scoring_weights, config.domain_reputation_file)
    
    score_result = scorer.calculate_credibility_score(
        model_prediction=fake_result,
        fact_check_results=fact_results,
        domain="example.com"
    )
    
    print(f"   Credibility score: {score_result['credibility_score']}/100")
    print(f"   Breakdown: {score_result['breakdown']}")
    
    # Test 5: Scraper
    print("\n5. Testing Web Scraper...")
    scraper = ArticleScraper()
    # Test with a simple page that should work
    scrape_result = scraper.extract_article("https://httpbin.org/html")
    if scrape_result['error']:
        print(f"   Scraping test: {scrape_result['error']} (this is expected for demo)")
    else:
        print(f"   Scraping successful: {len(scrape_result['text'] or '')} characters extracted")
    
    print("\n✅ All component tests completed!")
    print("\nNext steps:")
    print("1. Start the backend: cd backend && uvicorn app.main:app --reload")
    print("2. Start the frontend: cd frontend && npm install && npm start")
    print("3. Open http://localhost:3000 in your browser")
    
    return True

if __name__ == "__main__":
    try:
        success = test_components()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)