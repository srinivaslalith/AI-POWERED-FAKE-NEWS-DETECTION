import React, { useState } from 'react';

const InputForm = ({ onAnalyzeText, onAnalyzeUrl, loading }) => {
  const [inputType, setInputType] = useState('text'); // 'text' or 'url'
  const [textInput, setTextInput] = useState('');
  const [urlInput, setUrlInput] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (inputType === 'text') {
      if (textInput.trim().length < 10) {
        alert('Please enter at least 10 characters of text to analyze.');
        return;
      }
      await onAnalyzeText(textInput.trim());
    } else {
      if (!urlInput.trim()) {
        alert('Please enter a valid URL to analyze.');
        return;
      }
      await onAnalyzeUrl(urlInput.trim());
    }
  };

  const isFormValid = () => {
    if (inputType === 'text') {
      return textInput.trim().length >= 10;
    } else {
      return urlInput.trim().length > 0;
    }
  };

  const loadSampleText = () => {
    const sampleTexts = [
      "Breaking: Scientists discover miracle cure that reverses aging overnight — details inside. This revolutionary treatment has been hidden by Big Pharma for decades but leaked documents reveal the shocking truth.",
      "The Federal Reserve announced today that it will maintain interest rates at their current level following the conclusion of their two-day policy meeting. Fed Chair Jerome Powell cited ongoing economic uncertainty and inflation concerns as key factors in the decision."
    ];
    
    const randomSample = sampleTexts[Math.floor(Math.random() * sampleTexts.length)];
    setTextInput(randomSample);
  };

  return (
    <div className="input-section">
      <div className="input-toggle">
        <button
          type="button"
          className={`toggle-btn ${inputType === 'text' ? 'active' : ''}`}
          onClick={() => setInputType('text')}
        >
          📝 Analyze Text
        </button>
        <button
          type="button"
          className={`toggle-btn ${inputType === 'url' ? 'active' : ''}`}
          onClick={() => setInputType('url')}
        >
          🔗 Analyze URL
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        {inputType === 'text' ? (
          <div className="input-group">
            <label htmlFor="text-input">
              Article Text
              <button
                type="button"
                onClick={loadSampleText}
                style={{
                  marginLeft: '10px',
                  padding: '4px 8px',
                  fontSize: '12px',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Load Sample
              </button>
            </label>
            <textarea
              id="text-input"
              className="text-input"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Paste the article text you want to analyze for credibility..."
              disabled={loading}
            />
            <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
              {textInput.length} characters (minimum 10 required)
            </div>
          </div>
        ) : (
          <div className="input-group">
            <label htmlFor="url-input">Article URL</label>
            <input
              id="url-input"
              type="url"
              className="url-input"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="https://example.com/news-article"
              disabled={loading}
            />
            <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
              Enter a complete URL including http:// or https://
            </div>
          </div>
        )}

        <button
          type="submit"
          className="analyze-btn"
          disabled={loading || !isFormValid()}
        >
          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
              Analyzing...
            </div>
          ) : (
            `🔍 Analyze ${inputType === 'text' ? 'Text' : 'URL'}`
          )}
        </button>
      </form>
    </div>
  );
};

export default InputForm;