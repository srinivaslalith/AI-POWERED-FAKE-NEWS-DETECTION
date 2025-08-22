# 🔍 AI-Powered Fake News Detector

A modular FastAPI backend + React frontend prototype for detecting fake news using AI models, fact-checking APIs, and source reputation analysis.

## Features

- **AI-Powered Detection**: Uses HuggingFace transformers for fake news classification
- **Fact-Checking Integration**: Google Fact Check Tools API support with fallback
- **Source Reputation Analysis**: Domain-based credibility scoring
- **Sentence-Level Highlights**: Identifies suspicious content within articles
- **URL Scraping**: Automatic article extraction from web pages
- **Modern UI**: Beautiful React frontend with real-time analysis
- **History Tracking**: Local storage of analysis results
- **Modular Architecture**: Easy to extend with new models and data sources

## Quick Start

### 1. Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Run the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/docs`.

### 2. Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000`.

## Configuration

### Environment Variables

```bash
# Model configuration
export MODEL_NAME="mrm8488/bert-tiny-finetuned-fake-news-detection"
export MODEL_MAX_LENGTH=512

# Fact-checking API (optional)
export FACTCHECK_API_KEY="your_google_factcheck_api_key"

# Scoring weights (must sum to 1.0)
export WEIGHT_MODEL=0.5
export WEIGHT_FACTCHECK=0.3
export WEIGHT_SOURCE=0.2

# Domain reputation file
export DOMAIN_REPUTATION_FILE="domain_reputation.json"
```

### Configuration File

Edit `backend/config.yaml` to customize settings:

```yaml
model:
  name: "mrm8488/bert-tiny-finetuned-fake-news-detection"
  max_length: 512

factcheck:
  api_key: null  # Set your Google Fact Check Tools API key here
  enabled: false

scoring:
  weights:
    model_confidence: 0.5
    fact_check_evidence: 0.3
    source_reputation: 0.2
```

## API Endpoints

### POST `/predict`
Analyze article text for credibility.

**Request:**
```json
{
  "text": "Article text to analyze..."
}
```

**Response:**
```json
{
  "label": "Fake",
  "model_confidence": 0.89,
  "credibility_score": 22.5,
  "source": null,
  "source_reputation": null,
  "fact_check": [
    {
      "claim": "Fact-checking service unavailable",
      "url": "",
      "verdict": "API key required",
      "publisher": "System",
      "review_date": "",
      "mock": true
    }
  ],
  "highlights": [
    {
      "sentence": "This is suspicious sentence.",
      "suspicion_score": 0.92,
      "position": 0,
      "label": "Fake"
    }
  ],
  "explainability": {
    "method": "sentence_scoring",
    "details": "Analyzed 5 sentences using mrm8488/bert-tiny-finetuned-fake-news-detection"
  },
  "breakdown": {
    "model_score": 11.0,
    "factcheck_score": 50.0,
    "source_score": 50.0
  }
}
```

### POST `/predict-url`
Analyze article from URL.

**Request:**
```json
{
  "url": "https://example.com/news-article"
}
```

**Response:** Same as `/predict` but includes source information.

### GET `/health`
Check API health status.

### GET `/config`
Get current configuration and scoring methodology.

## Testing

### Run Unit Tests
```bash
cd backend
pytest tests/test_api.py -v
```

### Run API Tests
```bash
# Make sure API is running first
chmod +x scripts/test_requests.sh
./scripts/test_requests.sh
```

## Sample Inputs for Testing

### 1. Fake News Sample
```json
{
  "text": "Breaking: Scientists discover miracle cure that reverses aging overnight — details inside. This revolutionary treatment has been hidden by Big Pharma for decades but leaked documents reveal the shocking truth."
}
```

**Expected:** Low credibility score (< 30), "Fake" label

### 2. Real News Sample
```json
{
  "text": "The Federal Reserve announced today that it will maintain interest rates at their current level following the conclusion of their two-day policy meeting. Fed Chair Jerome Powell cited ongoing economic uncertainty and inflation concerns as key factors in the decision."
}
```

**Expected:** Higher credibility score (> 60), "Real" label

### 3. URL Sample
```json
{
  "url": "https://www.reuters.com/world/"
}
```

## Customization

### Swapping Models

1. Update `config.yaml` or set `MODEL_NAME` environment variable:
```yaml
model:
  name: "your-custom-model-name"
```

2. Ensure the model is compatible with HuggingFace text classification pipeline.

### Adding Fact-Check APIs

1. Get a Google Fact Check Tools API key from Google Cloud Console
2. Set the API key:
```bash
export FACTCHECK_API_KEY="your_api_key_here"
```

3. The system will automatically enable fact-checking when a valid API key is detected.

### Adjusting Scoring Weights

Modify weights in `config.yaml` (must sum to 1.0):
```yaml
scoring:
  weights:
    model_confidence: 0.6    # Increase AI model weight
    fact_check_evidence: 0.2  # Decrease fact-check weight
    source_reputation: 0.2   # Keep source weight same
```

### Adding Domain Reputation

Edit `backend/domain_reputation.json` to add new domains:
```json
{
  "newsite.com": 0.85,
  "unreliablesite.com": 0.15
}
```

Scores range from 0.0 (completely unreliable) to 1.0 (completely reliable).

## Architecture

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic schemas
│   ├── config.py            # Configuration management
│   ├── nlp_engine.py        # AI model integration
│   ├── factcheck_adapter.py # Fact-checking API
│   ├── scoring.py           # Credibility scoring
│   └── scraper.py           # Web scraping
├── tests/
│   └── test_api.py          # Unit tests
├── requirements.txt
├── config.yaml
└── domain_reputation.json

frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── InputForm.js     # Input form component
│   │   ├── ResultCard.js    # Results display
│   │   └── HistorySection.js # History management
│   ├── App.js               # Main application
│   ├── index.js             # React entry point
│   └── index.css            # Styles
└── package.json
```

## Production Deployment

### Backend
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend
```bash
# Build for production
npm run build

# Serve with any static file server
npx serve -s build -l 3000
```

## Troubleshooting

### Model Loading Issues
- Ensure you have sufficient memory (2GB+ recommended)
- Check internet connection for model download
- Try a smaller model if needed: `distilbert-base-uncased-finetuned-sst-2-english`

### CORS Issues
- Backend is configured to allow `localhost:3000`
- For production, update CORS origins in `app/main.py`

### Scraping Failures
- Some websites block automated scraping
- Try different URLs or implement more sophisticated scraping
- Check network connectivity

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Future Enhancements

- [ ] Multi-language model support
- [ ] Additional fact-checking APIs (Snopes, PolitiFact)
- [ ] Advanced explainability (LIME/SHAP)
- [ ] Real-time monitoring dashboard
- [ ] User feedback integration
- [ ] API rate limiting and authentication