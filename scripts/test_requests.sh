#!/bin/bash

# Test script for Fake News Detector API
# Make sure the API is running on http://localhost:8000

API_BASE="http://localhost:8000"

echo "🔍 Testing Fake News Detector API"
echo "=================================="

# Test 1: Health check
echo "1. Testing health endpoint..."
curl -s "$API_BASE/health" | jq . || echo "❌ Health check failed"
echo ""

# Test 2: Configuration
echo "2. Testing configuration endpoint..."
curl -s "$API_BASE/config" | jq . || echo "❌ Config check failed"
echo ""

# Test 3: Text prediction - Fake news sample
echo "3. Testing text prediction with fake news sample..."
curl -s -X POST "$API_BASE/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Breaking: Scientists discover miracle cure that reverses aging overnight — details inside. This revolutionary treatment has been hidden by Big Pharma for decades but leaked documents reveal the shocking truth."
  }' | jq . || echo "❌ Text prediction failed"
echo ""

# Test 4: Text prediction - Real news sample
echo "4. Testing text prediction with real news sample..."
curl -s -X POST "$API_BASE/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The Federal Reserve announced today that it will maintain interest rates at their current level following the conclusion of their two-day policy meeting. Fed Chair Jerome Powell cited ongoing economic uncertainty and inflation concerns as key factors in the decision."
  }' | jq . || echo "❌ Real news prediction failed"
echo ""

# Test 5: URL prediction (using a reliable news source)
echo "5. Testing URL prediction..."
curl -s -X POST "$API_BASE/predict-url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.reuters.com"
  }' | jq . || echo "❌ URL prediction failed (this may fail due to scraping)"
echo ""

# Test 6: Invalid inputs
echo "6. Testing error handling with invalid text..."
curl -s -X POST "$API_BASE/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": ""}' || echo "✅ Correctly rejected empty text"
echo ""

echo "7. Testing error handling with invalid URL..."
curl -s -X POST "$API_BASE/predict-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "not-a-url"}' || echo "✅ Correctly rejected invalid URL"
echo ""

echo "🎉 API testing complete!"
echo ""
echo "Expected results:"
echo "- Health check should return status: healthy"
echo "- Fake news sample should have low credibility score (< 50)"
echo "- Real news sample should have higher credibility score"
echo "- Invalid inputs should return 422 validation errors"