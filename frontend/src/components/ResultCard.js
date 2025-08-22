import React from 'react';

const ResultCard = ({ result }) => {
  if (!result) return null;

  const getLabelClass = (label) => {
    switch (label.toLowerCase()) {
      case 'fake':
        return 'label-fake';
      case 'real':
        return 'label-real';
      case 'biased':
        return 'label-biased';
      case 'satire':
        return 'label-satire';
      default:
        return 'label-fake';
    }
  };

  const getSuspicionClass = (score) => {
    if (score >= 0.7) return 'suspicion-high';
    if (score >= 0.4) return 'suspicion-medium';
    return 'suspicion-low';
  };

  const formatPercentage = (value) => {
    return Math.round(value * 100);
  };

  return (
    <div className="result-card">
      <div className="result-header">
        <div className={`label-badge ${getLabelClass(result.label)}`}>
          {result.label}
        </div>
        <div className="confidence-score">
          Model Confidence: {formatPercentage(result.model_confidence)}%
        </div>
      </div>

      <div className="credibility-section">
        <h3>Credibility Score</h3>
        <div className="credibility-gauge">
          <div 
            className="credibility-fill"
            style={{ width: `${result.credibility_score}%` }}
          ></div>
        </div>
        <div className="credibility-text">
          {result.credibility_score}/100
        </div>
        
        {result.source && (
          <div style={{ textAlign: 'center', marginTop: '10px', color: '#666' }}>
            Source: {result.source}
            {result.source_reputation && (
              <span style={{ marginLeft: '10px' }}>
                (Reputation: {formatPercentage(result.source_reputation)}%)
              </span>
            )}
          </div>
        )}
      </div>

      <div className="breakdown">
        <div className="breakdown-item">
          <h4>AI Model</h4>
          <div className="score">{result.breakdown.model_score}</div>
        </div>
        <div className="breakdown-item">
          <h4>Fact Check</h4>
          <div className="score">{result.breakdown.factcheck_score}</div>
        </div>
        <div className="breakdown-item">
          <h4>Source Rep.</h4>
          <div className="score">{result.breakdown.source_score}</div>
        </div>
      </div>

      {result.highlights && result.highlights.length > 0 && (
        <div className="highlights-section">
          <h3>🎯 Most Suspicious Sentences</h3>
          {result.highlights.map((highlight, index) => (
            <div
              key={index}
              className={`sentence-highlight ${getSuspicionClass(highlight.suspicion_score)}`}
            >
              <span className="suspicion-score">
                {formatPercentage(highlight.suspicion_score)}%
              </span>
              <div>{highlight.sentence}</div>
            </div>
          ))}
        </div>
      )}

      {result.fact_check && result.fact_check.length > 0 && (
        <div className="fact-check-section">
          <h3>📋 Fact Check Results</h3>
          {result.fact_check.map((factCheck, index) => (
            <div
              key={index}
              className={`fact-check-item ${factCheck.mock ? 'unavailable' : ''}`}
            >
              <div className="fact-check-verdict">
                {factCheck.verdict}
              </div>
              <div className="fact-check-publisher">
                {factCheck.publisher}
                {factCheck.review_date && ` • ${factCheck.review_date}`}
              </div>
              <div>
                <strong>Claim:</strong> {factCheck.claim}
              </div>
              {factCheck.url && !factCheck.mock && (
                <div style={{ marginTop: '10px' }}>
                  <a
                    href={factCheck.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="fact-check-link"
                  >
                    View Fact Check →
                  </a>
                </div>
              )}
              {factCheck.mock && (
                <div style={{ marginTop: '10px', fontStyle: 'italic', color: '#666' }}>
                  Fact-check lookup unavailable — install API key to enable.
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div style={{ marginTop: '25px', padding: '15px', background: 'white', borderRadius: '8px' }}>
        <h4 style={{ marginBottom: '10px', color: '#333' }}>📊 Analysis Details</h4>
        <div style={{ fontSize: '14px', color: '#666' }}>
          <div><strong>Method:</strong> {result.explainability.method}</div>
          <div><strong>Details:</strong> {result.explainability.details}</div>
          {result.metadata && (
            <>
              <div><strong>Text Length:</strong> {result.metadata.text_length} characters</div>
              <div><strong>Sentences Analyzed:</strong> {result.metadata.sentences_analyzed}</div>
              {result.metadata.model_truncated && (
                <div style={{ color: '#ffa502' }}>
                  <strong>Note:</strong> Text was truncated for model analysis
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultCard;