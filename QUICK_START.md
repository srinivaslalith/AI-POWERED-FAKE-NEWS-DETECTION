# 🚀 Quick Start Guide

## One-Command Demo

```bash
./start_demo.sh
```

This will automatically:
- Set up Python virtual environment
- Install all dependencies
- Start backend API on port 8000
- Start React frontend on port 3000
- Open your browser to the application

## Manual Setup (Step by Step)

### Backend (Terminal 1)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (Terminal 2)
```bash
cd frontend
npm install
npm start
```

## Test the API

```bash
# Run API tests
chmod +x scripts/test_requests.sh
./scripts/test_requests.sh

# Run unit tests
cd backend && pytest tests/test_api.py -v
```

## Sample Usage

### Text Analysis
1. Go to http://localhost:3000
2. Click "📝 Analyze Text"
3. Click "Load Sample" or paste your own text
4. Click "🔍 Analyze Text"
5. View credibility score and suspicious sentences

### URL Analysis
1. Click "🔗 Analyze URL"
2. Enter a news article URL
3. Click "🔍 Analyze URL"
4. View results with source reputation

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## Configuration

- Edit `backend/config.yaml` for settings
- Set `FACTCHECK_API_KEY` environment variable for fact-checking
- Modify `backend/domain_reputation.json` to add more news sources

## Troubleshooting

- **Model loading slow?** First run downloads ~100MB model
- **CORS errors?** Make sure both servers are running
- **Dependencies issues?** Use Python 3.8+ and Node.js 16+