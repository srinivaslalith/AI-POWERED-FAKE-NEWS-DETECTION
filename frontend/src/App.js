import React, { useState, useEffect } from 'react';
import axios from 'axios';
import InputForm from './components/InputForm';
import ResultCard from './components/ResultCard';
import HistorySection from './components/HistorySection';
import './index.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  // Load history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('fakeNewsHistory');
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory));
      } catch (e) {
        console.error('Failed to load history:', e);
      }
    }
  }, []);

  // Save history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('fakeNewsHistory', JSON.stringify(history));
  }, [history]);

  const addToHistory = (analysisResult, inputData) => {
    const historyItem = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      input: inputData,
      result: analysisResult
    };

    // Add to beginning of history and limit to 10 items
    setHistory(prev => [historyItem, ...prev.slice(0, 9)]);
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem('fakeNewsHistory');
  };

  const analyzeText = async (text) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE}/predict`, { text });
      const analysisResult = response.data;
      setResult(analysisResult);
      addToHistory(analysisResult, { type: 'text', content: text });
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Analysis failed';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const analyzeUrl = async (url) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE}/predict-url`, { url });
      const analysisResult = response.data;
      setResult(analysisResult);
      addToHistory(analysisResult, { type: 'url', content: url });
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'URL analysis failed';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const loadHistoryItem = (historyItem) => {
    setResult(historyItem.result);
    setError(null);
  };

  return (
    <div className="container">
      <header className="header">
        <h1>🔍 Fake News Detector</h1>
        <p>AI-powered credibility analysis for news articles</p>
      </header>

      <main className="main-card">
        <InputForm
          onAnalyzeText={analyzeText}
          onAnalyzeUrl={analyzeUrl}
          loading={loading}
        />

        {error && (
          <div className="error">
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <ResultCard result={result} />
        )}
      </main>

      <HistorySection
        history={history}
        onLoadHistoryItem={loadHistoryItem}
        onClearHistory={clearHistory}
      />
    </div>
  );
}

export default App;