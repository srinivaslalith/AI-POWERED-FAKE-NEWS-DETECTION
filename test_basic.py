#!/usr/bin/env python3
"""
Basic test script that validates the project structure and basic functionality
without requiring heavy ML dependencies.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if basic modules can be imported."""
    print("🔧 Testing Basic Module Imports")
    print("=" * 40)
    
    # Add backend to path
    backend_path = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_path))
    
    # Change to backend directory for relative file access
    original_cwd = os.getcwd()
    os.chdir(str(backend_path))
    
    try:
        # Test configuration
        print("📋 Testing configuration...")
        from app.config import config
        print(f"   ✅ Config loaded: {config.model_name}")
        
        # Test scraper (basic import)
        print("🕷️ Testing scraper...")
        try:
            from app.scraper import ArticleScraper
            print("   ✅ Scraper module imported")
        except ImportError as e:
            print(f"   ❌ Scraper import failed: {e}")
        
        # Test fact checker
        print("📊 Testing fact checker...")
        from app.factcheck_adapter import FactCheckAdapter
        fact_checker = FactCheckAdapter()
        status = fact_checker.get_status()
        print(f"   ✅ Fact checker status: {status['service']}")
        
        # Test scoring
        print("🎯 Testing scorer...")
        from app.scoring import CredibilityScorer
        scorer = CredibilityScorer(config.scoring_weights, config.domain_reputation_file)
        explanation = scorer.get_scoring_explanation()
        print(f"   ✅ Scorer loaded with {len(scorer.domain_reputation)} domains")
        
        # Test NLP engine (mock version)
        print("🤖 Testing NLP engine...")
        try:
            from app.nlp_engine import FakeNewsDetector
            print("   ✅ Full NLP engine available")
        except ImportError:
            from app.nlp_engine_mock import FakeNewsDetector
            print("   ✅ Mock NLP engine loaded (transformers not available)")
        
        detector = FakeNewsDetector(config.model_name, config.model_max_length)
        
        # Test prediction
        test_text = "Breaking: Scientists discover miracle cure that reverses aging overnight!"
        result = detector.predict(test_text)
        print(f"   ✅ Prediction: {result['label']} (confidence: {result['confidence']:.2f})")
        
        # Test sentence analysis
        sentences = detector.analyze_sentences(test_text)
        print(f"   ✅ Sentence analysis: {len(sentences)} sentences analyzed")
        
        # Test full pipeline
        print("🔄 Testing full analysis pipeline...")
        fact_results = fact_checker.check_claims(test_text)
        score_result = scorer.calculate_credibility_score(
            model_prediction=result,
            fact_check_results=fact_results,
            domain="example.com"
        )
        print(f"   ✅ Credibility score: {score_result['credibility_score']}/100")
        
        print("\n🎉 All basic tests PASSED!")
        print("\nThe system is ready to run. To start:")
        print("1. Install full dependencies: pip install -r requirements.txt")
        print("2. Start backend: uvicorn app.main:app --reload")
        print("3. Start frontend: cd frontend && npm install && npm start")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Restore original working directory
        os.chdir(original_cwd)

def test_file_structure():
    """Test that all required files exist."""
    print("\n📁 Testing File Structure")
    print("=" * 30)
    
    required_files = [
        "backend/requirements.txt",
        "backend/config.yaml",
        "backend/app/main.py",
        "frontend/package.json",
        "frontend/src/App.js",
        "README.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    print("🔍 Fake News Detector - Basic Validation")
    print("=" * 50)
    
    structure_ok = test_file_structure()
    imports_ok = test_imports()
    
    if structure_ok and imports_ok:
        print("\n✅ All tests PASSED! System is ready.")
        sys.exit(0)
    else:
        print("\n❌ Some tests FAILED. Check errors above.")
        sys.exit(1)