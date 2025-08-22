#!/usr/bin/env python3
"""
Lightweight validation script to check project structure.
This doesn't require ML dependencies to be installed.
"""

import os
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and print status."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (missing)")
        return False

def validate_project_structure():
    """Validate the complete project structure."""
    print("🔍 Validating Fake News Detector Project Structure")
    print("=" * 55)
    
    all_good = True
    
    # Backend files
    print("\n📁 Backend Files:")
    backend_files = [
        ("backend/requirements.txt", "Backend dependencies"),
        ("backend/config.yaml", "Configuration file"),
        ("backend/domain_reputation.json", "Domain reputation database"),
        ("backend/app/__init__.py", "App package init"),
        ("backend/app/main.py", "FastAPI main application"),
        ("backend/app/models.py", "Pydantic models"),
        ("backend/app/config.py", "Configuration module"),
        ("backend/app/nlp_engine.py", "NLP engine"),
        ("backend/app/factcheck_adapter.py", "Fact-check adapter"),
        ("backend/app/scoring.py", "Scoring module"),
        ("backend/app/scraper.py", "Web scraper"),
        ("backend/tests/__init__.py", "Tests package init"),
        ("backend/tests/test_api.py", "API unit tests"),
        ("backend/app.py", "Alternative entry point"),
    ]
    
    for filepath, description in backend_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # Frontend files
    print("\n🎨 Frontend Files:")
    frontend_files = [
        ("frontend/package.json", "Frontend dependencies"),
        ("frontend/public/index.html", "HTML template"),
        ("frontend/public/manifest.json", "PWA manifest"),
        ("frontend/src/index.js", "React entry point"),
        ("frontend/src/index.css", "Global styles"),
        ("frontend/src/App.js", "Main React component"),
        ("frontend/src/components/InputForm.js", "Input form component"),
        ("frontend/src/components/ResultCard.js", "Result display component"),
        ("frontend/src/components/HistorySection.js", "History component"),
    ]
    
    for filepath, description in frontend_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # Scripts and documentation
    print("\n📜 Scripts and Documentation:")
    other_files = [
        ("README.md", "Project documentation"),
        ("scripts/test_requests.sh", "API test script"),
        (".env.example", "Environment variables example"),
        ("start_demo.sh", "Demo startup script"),
        ("demo.py", "Component demo script"),
    ]
    
    for filepath, description in other_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    print("\n" + "=" * 55)
    if all_good:
        print("🎉 Project structure validation PASSED!")
        print("\nNext steps to run the demo:")
        print("1. cd backend && python -m venv venv && source venv/bin/activate")
        print("2. pip install -r requirements.txt")
        print("3. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("4. In another terminal: cd frontend && npm install && npm start")
        print("5. Open http://localhost:3000 in your browser")
        print("\nOr simply run: ./start_demo.sh")
    else:
        print("❌ Project structure validation FAILED!")
        print("Some files are missing. Please check the errors above.")
    
    return all_good

if __name__ == "__main__":
    success = validate_project_structure()
    exit(0 if success else 1)