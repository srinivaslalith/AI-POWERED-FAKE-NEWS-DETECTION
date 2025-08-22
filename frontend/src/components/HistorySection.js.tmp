import React from 'react';

const HistorySection = ({ history, onLoadHistoryItem, onClearHistory }) => {
  if (history.length === 0) {
    return null;
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getPreviewText = (item) => {
    if (item.input.type === 'url') {
      return `URL: ${item.input.content}`;
    } else {
      return item.input.content.length > 100 
        ? `${item.input.content.substring(0, 100)}...`
        : item.input.content;
    }
  };

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

  return (
    <div className="history-section">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>📚 Recent Analysis History</h2>
        <button className="clear-history" onClick={onClearHistory}>
          Clear History
        </button>
      </div>
      
      <div className="history-list">
        {history.map((item) => (
          <div
            key={item.id}
            className="history-item"
            onClick={() => onLoadHistoryItem(item)}
          >
            <div className="history-item-header">
              <div className={`label-badge ${getLabelClass(item.result.label)}`}>
                {item.result.label}
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>
                {formatTimestamp(item.timestamp)}
              </div>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <div style={{ fontWeight: '600' }}>
                Credibility: {item.result.credibility_score}/100
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>
                Confidence: {Math.round(item.result.model_confidence * 100)}%
              </div>
            </div>
            
            <div className="history-item-preview">
              {getPreviewText(item)}
            </div>
            
            {item.result.source && (
              <div style={{ fontSize: '12px', color: '#888', marginTop: '5px' }}>
                Source: {item.result.source}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default HistorySection;