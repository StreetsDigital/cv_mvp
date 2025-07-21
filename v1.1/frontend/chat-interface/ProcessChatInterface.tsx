/**
 * ProcessChatInterface - Real-time process visualization component
 * Shows step-by-step AI analysis with human intervention options
 */

import React, { useState, useEffect, useRef } from 'react';
import { ProcessMessage } from './ProcessMessage';
import { HumanInterventionPanel } from './HumanInterventionPanel';
import { ProgressIndicator } from './ProgressIndicator';

interface ProcessMessage {
  step: number;
  title: string;
  description: string;
  timestamp: string;
  confidence?: number;
  data?: any;
  human_intervention_available?: boolean;
  type: string;
}

interface ProcessChatInterfaceProps {
  sessionId: string;
  onHumanIntervention: (step: any) => void;
  onAnalysisComplete: (results: any) => void;
  websocketUrl?: string;
}

export const ProcessChatInterface: React.FC<ProcessChatInterfaceProps> = ({
  sessionId,
  onHumanIntervention,
  onAnalysisComplete,
  websocketUrl = 'ws://localhost:8000'
}) => {
  const [messages, setMessages] = useState<ProcessMessage[]>([]);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [humanInputRequired, setHumanInputRequired] = useState<boolean>(false);
  const [interventionData, setInterventionData] = useState<any>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [analysisComplete, setAnalysisComplete] = useState<boolean>(false);
  
  const websocketRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Establish WebSocket connection
    const ws = new WebSocket(`${websocketUrl}/ws/analysis/${sessionId}`);
    websocketRef.current = ws;

    ws.onopen = () => {
      setConnectionStatus('connected');
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      switch (message.type) {
        case 'process_update':
          setMessages(prev => [...prev, message]);
          setCurrentStep(message.title);
          break;
          
        case 'human_intervention_required':
          setHumanInputRequired(true);
          setInterventionData(message);
          onHumanIntervention(message);
          break;
          
        case 'analysis_complete':
          setAnalysisComplete(true);
          onAnalysisComplete(message.result);
          break;
          
        case 'analysis_error':
          console.error('Analysis error:', message.error);
          setMessages(prev => [...prev, {
            step: prev.length + 1,
            title: '❌ Analysis Error',
            description: `Error: ${message.error}`,
            timestamp: message.timestamp,
            type: 'error'
          }]);
          break;
          
        case 'connection_established':
          console.log('Connection established:', message.connection_id);
          break;
          
        default:
          console.log('Unknown message type:', message.type);
      }
    };

    ws.onclose = () => {
      setConnectionStatus('disconnected');
      console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('disconnected');
    };

    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, [sessionId, websocketUrl, onHumanIntervention, onAnalysisComplete]);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startAnalysis = (cvText: string, jobDescription: string, detailLevel: string = 'moderate') => {
    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
      websocketRef.current.send(JSON.stringify({
        type: 'start_analysis',
        data: {
          cv_text: cvText,
          job_description: jobDescription,
          detail_level: detailLevel
        }
      }));
    }
  };

  const handleHumanDecision = (decision: string, data?: any) => {
    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
      websocketRef.current.send(JSON.stringify({
        type: 'human_intervention',
        data: {
          intervention_type: interventionData?.intervention_type,
          decision: decision,
          data: data
        }
      }));
      
      setHumanInputRequired(false);
      setInterventionData(null);
    }
  };

  const getConnectionStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected': return '🟢';
      case 'connecting': return '🟡';
      case 'disconnected': return '🔴';
      default: return '⚪';
    }
  };

  return (
    <div className="process-chat-container">
      <div className="chat-header">
        <div className="header-content">
          <h3>🔍 AI Process Explanation</h3>
          <div className="connection-status">
            {getConnectionStatusIcon()} {connectionStatus}
          </div>
        </div>
        
        <ProgressIndicator 
          currentStep={messages.length}
          totalSteps={15}
          currentStepTitle={currentStep}
          analysisComplete={analysisComplete}
        />
      </div>

      <div className="chat-messages" style={{ maxHeight: '500px', overflowY: 'auto' }}>
        {messages.map((message, index) => (
          <ProcessMessage 
            key={index} 
            message={message}
            isLatest={index === messages.length - 1}
          />
        ))}
        
        {messages.length === 0 && connectionStatus === 'connected' && (
          <div className="welcome-message">
            <div className="message-content">
              <h4>🚀 Ready to Start Analysis</h4>
              <p>Connected successfully. Upload a CV and job description to begin the enhanced analysis process.</p>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {humanInputRequired && interventionData && (
        <HumanInterventionPanel 
          interventionData={interventionData}
          onDecision={handleHumanDecision}
          onCancel={() => {
            setHumanInputRequired(false);
            setInterventionData(null);
          }}
        />
      )}
      
      {analysisComplete && (
        <div className="analysis-complete">
          <div className="completion-message">
            ✅ Analysis Complete! Check the results panel for detailed insights.
          </div>
        </div>
      )}
    </div>
  );
};

// Expose startAnalysis method for external use
ProcessChatInterface.displayName = 'ProcessChatInterface';
