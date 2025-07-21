/**
 * HumanInterventionPanel - Interactive panel for human-in-the-loop decisions
 * Allows users to review and modify AI decisions during analysis
 */

import React, { useState } from 'react';

interface InterventionData {
  intervention_type: string;
  step: number;
  data: any;
  options: Array<{
    value: string;
    label: string;
  }>;
}

interface HumanInterventionPanelProps {
  interventionData: InterventionData;
  onDecision: (decision: string, data?: any) => void;
  onCancel: () => void;
}

export const HumanInterventionPanel: React.FC<HumanInterventionPanelProps> = ({
  interventionData,
  onDecision,
  onCancel
}) => {
  const [selectedOption, setSelectedOption] = useState<string>('');
  const [customData, setCustomData] = useState<any>({});
  const [showCustomInput, setShowCustomInput] = useState<boolean>(false);

  const getInterventionTitle = (type: string) => {
    const titles: Record<string, string> = {
      'keyword_review': '🔤 Review Keywords',
      'scoring_review': '📊 Review Scoring',
      'pattern_validation': '🔍 Validate Patterns',
      'industry_classification': '🏥 Industry Classification',
      'skill_categorization': '📋 Skill Categories'
    };
    return titles[type] || '⚙️ Review Required';
  };

  const getInterventionDescription = (type: string) => {
    const descriptions: Record<string, string> = {
      'keyword_review': 'The AI has detected keywords in the CV. Please review and confirm which ones are most relevant.',
      'scoring_review': 'Review the calculated scores for accuracy. You can adjust if needed.',
      'pattern_validation': 'The AI detected certain patterns. Please validate these findings.',
      'industry_classification': 'Confirm the industry classification is accurate.',
      'skill_categorization': 'Review how skills were categorized.'
    };
    return descriptions[type] || 'Please review this step and provide feedback.';
  };

  const handleSubmit = () => {
    if (!selectedOption) return;
    
    let submissionData = customData;
    
    // Include any custom modifications based on intervention type
    if (interventionData.intervention_type === 'keyword_review' && customData.selectedKeywords) {
      submissionData = {
        ...submissionData,
        modified_keywords: customData.selectedKeywords
      };
    }
    
    onDecision(selectedOption, submissionData);
  };

  const renderCustomInputs = () => {
    if (!showCustomInput) return null;

    switch (interventionData.intervention_type) {
      case 'keyword_review':
        return (
          <div className="custom-inputs">
            <h5>Keyword Priority Adjustment:</h5>
            <div className="keywords-review">
              {interventionData.data.keywords_found?.map((keyword: any, idx: number) => (
                <label key={idx} className="keyword-checkbox">
                  <input
                    type="checkbox"
                    checked={customData.selectedKeywords?.includes(keyword.keyword || keyword) || false}
                    onChange={(e) => {
                      const keywordText = keyword.keyword || keyword;
                      const selected = customData.selectedKeywords || [];
                      if (e.target.checked) {
                        setCustomData({
                          ...customData,
                          selectedKeywords: [...selected, keywordText]
                        });
                      } else {
                        setCustomData({
                          ...customData,
                          selectedKeywords: selected.filter((k: string) => k !== keywordText)
                        });
                      }
                    }}
                  />
                  <span>{keyword.keyword || keyword}</span>
                  {keyword.confidence && (
                    <span className="confidence-mini">
                      ({Math.round(keyword.confidence * 100)}%)
                    </span>
                  )}
                </label>
              ))}
            </div>
          </div>
        );
      
      case 'scoring_review':
        return (
          <div className="custom-inputs">
            <h5>Score Adjustments:</h5>
            {Object.entries(interventionData.data.score_breakdown || {}).map(([category, score]: [string, any]) => (
              <div key={category} className="score-adjuster">
                <label>{category}:</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={customData[`${category}_score`] || score}
                  onChange={(e) => setCustomData({
                    ...customData,
                    [`${category}_score`]: parseInt(e.target.value)
                  })}
                />
                <span>{customData[`${category}_score`] || score}%</span>
              </div>
            ))}
          </div>
        );
      
      default:
        return (
          <div className="custom-inputs">
            <textarea
              placeholder="Add your comments or modifications..."
              value={customData.comments || ''}
              onChange={(e) => setCustomData({
                ...customData,
                comments: e.target.value
              })}
              rows={3}
            />
          </div>
        );
    }
  };

  return (
    <div className="human-intervention-panel">
      <div className="intervention-overlay" onClick={onCancel} />
      
      <div className="intervention-modal">
        <div className="intervention-header">
          <h3>{getInterventionTitle(interventionData.intervention_type)}</h3>
          <button className="close-button" onClick={onCancel}>×</button>
        </div>
        
        <div className="intervention-content">
          <p className="intervention-description">
            {getInterventionDescription(interventionData.intervention_type)}
          </p>
          
          <div className="intervention-data">
            {interventionData.data && (
              <div className="data-preview">
                <h5>Current Analysis:</h5>
                <div className="data-summary">
                  {interventionData.intervention_type === 'keyword_review' && (
                    <p>Found {interventionData.data.keywords_found?.length || 0} keywords</p>
                  )}
                  {interventionData.intervention_type === 'scoring_review' && (
                    <p>Overall score: {interventionData.data.overall_score || 'N/A'}%</p>
                  )}
                  {interventionData.intervention_type === 'pattern_validation' && (
                    <p>Patterns detected: {Object.keys(interventionData.data.patterns_detected || {}).length}</p>
                  )}
                </div>
              </div>
            )}
          </div>
          
          <div className="intervention-options">
            <h5>Choose an action:</h5>
            {interventionData.options.map((option, idx) => (
              <label key={idx} className="option-radio">
                <input
                  type="radio"
                  name="intervention-option"
                  value={option.value}
                  checked={selectedOption === option.value}
                  onChange={(e) => {
                    setSelectedOption(e.target.value);
                    setShowCustomInput(e.target.value.includes('adjust') || e.target.value.includes('review'));
                  }}
                />
                <span>{option.label}</span>
              </label>
            ))}
          </div>
          
          {renderCustomInputs()}
          
          <div className="intervention-actions">
            <button 
              className="btn-cancel" 
              onClick={onCancel}
            >
              Cancel
            </button>
            <button 
              className="btn-submit" 
              onClick={handleSubmit}
              disabled={!selectedOption}
            >
              Continue Analysis
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
