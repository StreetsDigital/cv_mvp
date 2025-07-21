/**
 * ProcessMessage - Individual process step display component
 * Shows step details with expandable content and confidence indicators
 */

import React, { useState } from 'react';

interface ProcessMessageProps {
  message: {
    step: number;
    title: string;
    description: string;
    timestamp: string;
    confidence?: number;
    data?: any;
    human_intervention_available?: boolean;
    type: string;
  };
  isLatest?: boolean;
}

export const ProcessMessage: React.FC<ProcessMessageProps> = ({ message, isLatest = false }) => {
  const [expanded, setExpanded] = useState(false);

  const getMessageTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      'process_update': '⚙️',
      'keyword_extraction': '🔤',
      'skill_categorization': '📊',
      'pattern_matching': '🔍',
      'industry_analysis': '🏥',
      'scoring': '📊',
      'recommendations': '💡',
      'error': '❌',
      'completion': '✅'
    };
    return icons[type] || '📝';
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return '#gray';
    if (confidence > 0.8) return '#22c55e'; // green
    if (confidence > 0.6) return '#f59e0b'; // orange
    return '#ef4444'; // red
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const renderDataDetails = () => {
    if (!message.data || !expanded) return null;

    const { data } = message;

    // Keyword extraction details
    if (data.keywords_found) {
      return (
        <div className="data-details">
          <h5>Keywords Detected:</h5>
          <div className="keywords-grid">
            {data.keywords_found.slice(0, 8).map((keyword: any, idx: number) => (
              <span key={idx} className="keyword-badge">
                {keyword.keyword || keyword} 
                {keyword.confidence && (
                  <span className="confidence-mini">
                    {Math.round(keyword.confidence * 100)}%
                  </span>
                )}
              </span>
            ))}
            {data.keywords_found.length > 8 && (
              <span className="more-keywords">
                +{data.keywords_found.length - 8} more
              </span>
            )}
          </div>
        </div>
      );
    }

    // Skill categorization details
    if (data.skills_found) {
      return (
        <div className="data-details">
          <h5>Skills in {data.category}:</h5>
          <div className="skills-list">
            {data.skills_found.map((skill: string, idx: number) => (
              <span key={idx} className="skill-tag">{skill}</span>
            ))}
          </div>
          <div className="score-explanation">
            <strong>Score: {data.category_score}%</strong> - {data.evidence_strength} evidence
          </div>
        </div>
      );
    }

    // Pattern matching details
    if (data.patterns_detected) {
      return (
        <div className="data-details">
          <h5>Pattern Analysis:</h5>
          <div className="patterns-grid">
            {Object.entries(data.patterns_detected).map(([pattern, info]: [string, any]) => (
              <div key={pattern} className="pattern-item">
                <span className="pattern-name">{pattern.replace('_', ' ')}</span>
                <span className="pattern-status">
                  {info.detected ? '✅' : '❌'} ({Math.round(info.confidence * 100)}%)
                </span>
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Industry analysis details
    if (data.industry && data.evidence) {
      return (
        <div className="data-details">
          <h5>Industry: {data.industry}</h5>
          <div className="evidence-list">
            {data.evidence.slice(0, 3).map((evidence: string, idx: number) => (
              <div key={idx} className="evidence-item">• {evidence}</div>
            ))}
          </div>
        </div>
      );
    }

    // Score breakdown details
    if (data.score_breakdown) {
      return (
        <div className="data-details">
          <h5>Score Breakdown:</h5>
          <div className="score-grid">
            {Object.entries(data.score_breakdown).map(([category, score]: [string, any]) => (
              <div key={category} className="score-item">
                <span className="score-category">{category}</span>
                <span className="score-value">{score}%</span>
                <div className="score-bar">
                  <div 
                    className="score-fill" 
                    style={{ width: `${score}%`, backgroundColor: getConfidenceColor(score / 100) }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Generic data display
    return (
      <div className="data-details">
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    );
  };

  return (
    <div className={`process-message ${message.type} ${isLatest ? 'latest' : ''}`}>
      <div className="message-header" onClick={() => setExpanded(!expanded)}>
        <div className="header-left">
          <span className="step-icon">{getMessageTypeIcon(message.type)}</span>
          <span className="step-number">#{message.step}</span>
          <h4 className="message-title">{message.title}</h4>
        </div>
        
        <div className="header-right">
          {message.confidence && (
            <span 
              className="confidence-badge"
              style={{ backgroundColor: getConfidenceColor(message.confidence) }}
            >
              {Math.round(message.confidence * 100)}%
            </span>
          )}
          <span className="timestamp">{formatTimestamp(message.timestamp)}</span>
          <span className="expand-icon">{expanded ? '▼' : '▶'}</span>
        </div>
      </div>

      <div className="message-content">
        <p className="description">{message.description}</p>
        
        {message.human_intervention_available && (
          <div className="intervention-notice">
            ⚙️ Human review available for this step
          </div>
        )}
        
        {expanded && renderDataDetails()}
      </div>
    </div>
  );
};
