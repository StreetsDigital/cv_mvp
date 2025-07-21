/**
 * Single unified interface layout - no chat/analysis toggle
 * Integrated process visualization with CV input
 */

import React, { useState, useRef } from 'react';
import { ProcessChatInterface } from '../chat-interface/ProcessChatInterface';
import { AdvancedSettings } from '../components/AdvancedSettings';
import { ResultsPanel } from '../components/ResultsPanel';

interface CVAnalysisLayoutProps {
  websocketUrl?: string;
}

export const CVAnalysisLayout: React.FC<CVAnalysisLayoutProps> = ({
  websocketUrl = 'ws://localhost:8000'
}) => {
  const [cvText, setCvText] = useState<string>('');
  const [jobDescription, setJobDescription] = useState<string>('');
  const [sessionId, setSessionId] = useState<string>('');
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState<boolean>(false);
  const [detailLevel, setDetailLevel] = useState<string>('moderate');
  
  const processChatRef = useRef<any>(null);

  const generateSessionId = () => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  const handleStartAnalysis = () => {
    if (!cvText.trim() || !jobDescription.trim()) {
      alert('Please provide both CV text and job description');
      return;
    }

    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
    setIsAnalyzing(true);
    setAnalysisResults(null);

    // Start analysis via ProcessChatInterface
    if (processChatRef.current) {
      processChatRef.current.startAnalysis(cvText, jobDescription, detailLevel);
    }
  };

  const handleAnalysisComplete = (results: any) => {
    setAnalysisResults(results);
    setIsAnalyzing(false);
  };

  const handleHumanIntervention = (interventionData: any) => {
    console.log('Human intervention requested:', interventionData);
    // The ProcessChatInterface will handle the intervention UI
  };

  const clearAll = () => {
    setCvText('');
    setJobDescription('');
    setSessionId('');
    setAnalysisResults(null);
    setIsAnalyzing(false);
  };

  return (
    <div className="cv-analysis-layout">
      <header className="layout-header">
        <h1>🔍 Enhanced CV Screening</h1>
        <p>AI-powered candidate analysis with real-time process transparency</p>
        
        <div className="header-controls">
          <button 
            className="btn-settings"
            onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
          >
            ⚙️ Advanced Settings
          </button>
          {(cvText || jobDescription) && (
            <button className="btn-clear" onClick={clearAll}>
              🗑️ Clear All
            </button>
          )}
        </div>
      </header>

      {showAdvancedSettings && (
        <AdvancedSettings 
          detailLevel={detailLevel}
          onDetailLevelChange={setDetailLevel}
          onClose={() => setShowAdvancedSettings(false)}
        />
      )}

      <div className="layout-content">
        <div className="input-section">
          <div className="cv-input-panel">
            <h3>📄 CV Text</h3>
            <textarea
              value={cvText}
              onChange={(e) => setCvText(e.target.value)}
              placeholder="Paste the candidate's CV text here..."
              rows={12}
              disabled={isAnalyzing}
            />
          </div>

          <div className="job-input-panel">
            <h3>💼 Job Description</h3>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description here..."
              rows={8}
              disabled={isAnalyzing}
            />
            
            <button 
              className={`analyze-btn ${isAnalyzing ? 'analyzing' : ''}`}
              onClick={handleStartAnalysis}
              disabled={isAnalyzing || !cvText.trim() || !jobDescription.trim()}
            >
              {isAnalyzing ? (
                <>🔄 Analyzing...</>
              ) : (
                <>🚀 Start Enhanced Analysis</>
              )}
            </button>
          </div>
        </div>

        <div className="process-section">
          {sessionId && (
            <ProcessChatInterface
              ref={processChatRef}
              sessionId={sessionId}
              onHumanIntervention={handleHumanIntervention}
              onAnalysisComplete={handleAnalysisComplete}
              websocketUrl={websocketUrl}
            />
          )}
        </div>
      </div>

      {analysisResults && (
        <div className="results-section">
          <ResultsPanel 
            results={analysisResults}
            sessionId={sessionId}
          />
        </div>
      )}

      <footer className="layout-footer">
        <div className="status-bar">
          <span>Status: {isAnalyzing ? 'Analyzing' : 'Ready'}</span>
          {sessionId && <span>Session: {sessionId}</span>}
        </div>
      </footer>
    </div>
  );
};
