/**
 * Real-Time CV Analyzer with WebSocket Integration
 * V1.1 Enhanced CV Screening Frontend Component
 */

class RealtimeCVAnalyzer {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.websocket = null;
        this.processSteps = [];
        this.isAnalyzing = false;
        this.interventionPromise = null;
        
        this.initializeUI();
        this.bindEvents();
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }
    
    initializeUI() {
        // Create real-time analysis interface
        const container = document.getElementById('cv-analyzer-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="realtime-analyzer">
                <div class="analyzer-header">
                    <h2>🔍 Real-Time CV Analysis</h2>
                    <div class="session-info">
                        <span class="session-id">Session: ${this.sessionId}</span>
                        <div class="connection-status" id="connection-status">
                            <span class="status-indicator disconnected"></span>
                            <span class="status-text">Disconnected</span>
                        </div>
                    </div>
                </div>
                
                <div class="analyzer-content">
                    <!-- Input Section -->
                    <div class="input-section">
                        <div class="input-group">
                            <label for="cv-text">CV Text:</label>
                            <textarea 
                                id="cv-text" 
                                placeholder="Paste CV content here..."
                                rows="10"
                                cols="50"
                            ></textarea>
                        </div>
                        
                        <div class="input-group">
                            <label for="job-description">Job Description:</label>
                            <textarea 
                                id="job-description" 
                                placeholder="Paste job description here..."
                                rows="8"
                                cols="50"
                            ></textarea>
                        </div>
                        
                        <button id="start-analysis" class="btn-primary" disabled>
                            Start Real-Time Analysis
                        </button>
                    </div>
                    
                    <!-- Process Visualization Section -->
                    <div class="process-section">
                        <div class="process-header">
                            <h3>📊 Analysis Progress</h3>
                            <div class="progress-bar">
                                <div class="progress-fill" id="progress-fill"></div>
                            </div>
                        </div>
                        
                        <div class="process-timeline" id="process-timeline">
                            <!-- Process steps will be added here dynamically -->
                        </div>
                    </div>
                    
                    <!-- Intervention Panel -->
                    <div class="intervention-panel" id="intervention-panel" style="display: none;">
                        <div class="intervention-header">
                            <h4>🤔 Human Input Needed</h4>
                        </div>
                        <div class="intervention-content" id="intervention-content">
                            <!-- Intervention requests will appear here -->
                        </div>
                    </div>
                    
                    <!-- Results Section -->
                    <div class="results-section" id="results-section" style="display: none;">
                        <h3>📋 Analysis Results</h3>
                        <div class="results-content" id="results-content">
                            <!-- Final results will appear here -->
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.addStyles();
    }
    
    addStyles() {
        const styles = `
            .realtime-analyzer {
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            .analyzer-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 15px;
                border-bottom: 2px solid #e9ecef;
            }
            
            .session-info {
                display: flex;
                align-items: center;
                gap: 15px;
            }
            
            .connection-status {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .status-indicator {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #dc3545;
            }
            
            .status-indicator.connected {
                background: #28a745;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            
            .analyzer-content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
            }
            
            .input-section {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            
            .input-group {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .input-group label {
                font-weight: bold;
                color: #495057;
            }
            
            .input-group textarea {
                padding: 12px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                resize: vertical;
            }
            
            .input-group textarea:focus {
                border-color: #007bff;
                outline: none;
                box-shadow: 0 0 0 3px rgba(0,123,255,0.25);
            }
            
            .btn-primary {
                padding: 15px 30px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn-primary:hover:not(:disabled) {
                background: #0056b3;
                transform: translateY(-1px);
            }
            
            .btn-primary:disabled {
                background: #6c757d;
                cursor: not-allowed;
            }
            
            .process-section {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: #e9ecef;
                border-radius: 4px;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #007bff, #28a745);
                width: 0%;
                transition: width 0.3s ease;
            }
            
            .process-timeline {
                display: flex;
                flex-direction: column;
                gap: 15px;
                max-height: 400px;
                overflow-y: auto;
                padding: 15px;
                background: white;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }
            
            .process-step {
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #007bff;
                background: #f8f9fa;
                transition: all 0.3s ease;
            }
            
            .process-step.completed {
                border-left-color: #28a745;
                background: #d4edda;
            }
            
            .process-step.failed {
                border-left-color: #dc3545;
                background: #f8d7da;
            }
            
            .process-step.in-progress {
                border-left-color: #ffc107;
                background: #fff3cd;
                animation: shimmer 1.5s infinite;
            }
            
            @keyframes shimmer {
                0% { background-position: -200px 0; }
                100% { background-position: calc(200px + 100%) 0; }
            }
            
            .step-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            
            .step-title {
                font-weight: bold;
                color: #495057;
            }
            
            .step-confidence {
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                color: white;
            }
            
            .step-confidence.high {
                background: #28a745;
            }
            
            .step-confidence.medium {
                background: #ffc107;
                color: #212529;
            }
            
            .step-confidence.low {
                background: #dc3545;
            }
            
            .step-explanation {
                color: #6c757d;
                line-height: 1.5;
                margin-bottom: 10px;
            }
            
            .step-evidence {
                margin-top: 10px;
            }
            
            .evidence-list {
                list-style: none;
                padding: 0;
                margin: 5px 0;
            }
            
            .evidence-list li {
                padding: 2px 0;
                font-size: 14px;
                color: #495057;
            }
            
            .intervention-panel {
                grid-column: 1 / -1;
                background: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
            }
            
            .intervention-header h4 {
                margin: 0 0 15px 0;
                color: #856404;
            }
            
            .intervention-options {
                display: flex;
                gap: 10px;
                margin-top: 15px;
            }
            
            .btn-intervention {
                padding: 8px 16px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background: white;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn-intervention:hover {
                background: #f8f9fa;
                border-color: #adb5bd;
            }
            
            .btn-intervention.selected {
                background: #007bff;
                color: white;
                border-color: #007bff;
            }
            
            .results-section {
                grid-column: 1 / -1;
                background: white;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
                border: 1px solid #dee2e6;
            }
            
            .score-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            
            .score-card {
                background: #f8f9fa;
                border-radius: 6px;
                padding: 15px;
                text-align: center;
                border-left: 4px solid #007bff;
            }
            
            .score-value {
                font-size: 24px;
                font-weight: bold;
                color: #007bff;
                margin-bottom: 5px;
            }
            
            .score-label {
                font-size: 14px;
                color: #6c757d;
            }
            
            @media (max-width: 768px) {
                .analyzer-content {
                    grid-template-columns: 1fr;
                }
                
                .analyzer-header {
                    flex-direction: column;
                    gap: 15px;
                    text-align: center;
                }
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    bindEvents() {
        // Start analysis button
        document.getElementById('start-analysis').addEventListener('click', () => {
            this.startAnalysis();
        });
        
        // Enable/disable analysis button based on input
        const cvText = document.getElementById('cv-text');
        const jobDesc = document.getElementById('job-description');
        
        const checkInputs = () => {
            const button = document.getElementById('start-analysis');
            const hasCV = cvText.value.trim().length > 0;
            const hasJob = jobDesc.value.trim().length > 0;
            const connected = this.websocket && this.websocket.readyState === WebSocket.OPEN;
            
            button.disabled = !(hasCV && hasJob && connected && !this.isAnalyzing);
        };
        
        cvText.addEventListener('input', checkInputs);
        jobDesc.addEventListener('input', checkInputs);
        
        // Auto-connect WebSocket when page loads
        setTimeout(() => this.connectWebSocket(), 1000);
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/analysis?session_id=${this.sessionId}`;
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.updateConnectionStatus(true);
                this.checkInputs();
            };
            
            this.websocket.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleWebSocketMessage(message);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateConnectionStatus(false);
                this.checkInputs();
                
                // Auto-reconnect after 3 seconds
                setTimeout(() => this.connectWebSocket(), 3000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
            };
            
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.updateConnectionStatus(false);
        }
    }
    
    updateConnectionStatus(connected) {
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.querySelector('.status-text');
        
        if (connected) {
            statusIndicator.classList.add('connected');
            statusText.textContent = 'Connected';
        } else {
            statusIndicator.classList.remove('connected');
            statusText.textContent = 'Disconnected';
        }
    }
    
    checkInputs() {
        const button = document.getElementById('start-analysis');
        const cvText = document.getElementById('cv-text').value.trim();
        const jobDesc = document.getElementById('job-description').value.trim();
        const connected = this.websocket && this.websocket.readyState === WebSocket.OPEN;
        
        button.disabled = !(cvText && jobDesc && connected && !this.isAnalyzing);
    }
    
    async startAnalysis() {
        const cvText = document.getElementById('cv-text').value.trim();
        const jobDescription = document.getElementById('job-description').value.trim();
        
        if (!cvText || !jobDescription) {
            alert('Please provide both CV text and job description');
            return;
        }
        
        this.isAnalyzing = true;
        this.processSteps = [];
        this.clearTimeline();
        this.hideResults();
        
        // Update UI
        document.getElementById('start-analysis').disabled = true;
        document.getElementById('start-analysis').textContent = 'Analyzing...';
        
        try {
            // Start real-time analysis
            const response = await fetch('/api/analyze-realtime', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    cv_text: cvText,
                    job_description: jobDescription
                }),
                params: new URLSearchParams({
                    session_id: this.sessionId
                })
            });
            
            if (response.ok) {
                const results = await response.json();
                this.displayResults(results);
            } else {
                throw new Error(`Analysis failed: ${response.statusText}`);
            }
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.addProcessStep({
                step_name: 'Analysis Error',
                status: 'failed',
                confidence: 0,
                explanation: `Error: ${error.message}`
            });
        } finally {
            this.isAnalyzing = false;
            document.getElementById('start-analysis').disabled = false;
            document.getElementById('start-analysis').textContent = 'Start Real-Time Analysis';
            this.checkInputs();
        }
    }
    
    handleWebSocketMessage(message) {
        console.log('WebSocket message:', message);
        
        switch (message.type) {
            case 'connection_established':
                console.log('Connection established:', message.connection_id);
                break;
                
            case 'process_update':
                this.handleProcessUpdate(message.data);
                break;
                
            case 'intervention_request':
                this.handleInterventionRequest(message.data);
                break;
                
            case 'error':
                console.error('WebSocket error:', message.error);
                break;
                
            default:
                console.log('Unknown message type:', message.type);
        }
    }
    
    handleProcessUpdate(update) {
        this.addProcessStep(update);
        this.updateProgress();
    }
    
    addProcessStep(stepData) {
        const timeline = document.getElementById('process-timeline');
        const stepElement = document.createElement('div');
        stepElement.className = `process-step ${stepData.status}`;
        stepElement.id = `step-${stepData.step_id || stepData.step_name.replace(/\\s+/g, '-')}`;
        
        const confidenceClass = stepData.confidence >= 0.8 ? 'high' : 
                               stepData.confidence >= 0.6 ? 'medium' : 'low';
        
        stepElement.innerHTML = `
            <div class="step-header">
                <span class="step-title">${stepData.step_name}</span>
                <span class="step-confidence ${confidenceClass}">
                    ${Math.round(stepData.confidence * 100)}%
                </span>
            </div>
            <div class="step-explanation">${stepData.explanation}</div>
            ${stepData.details && stepData.details.evidence ? `
                <div class="step-evidence">
                    <strong>Evidence:</strong>
                    <ul class="evidence-list">
                        ${stepData.details.evidence.map(item => `<li>• ${item}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
        
        // Update existing step or add new one
        const existingStep = document.getElementById(stepElement.id);
        if (existingStep) {
            existingStep.replaceWith(stepElement);
        } else {
            timeline.appendChild(stepElement);
        }
        
        // Scroll to latest step
        stepElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        this.processSteps.push(stepData);
    }
    
    updateProgress() {
        const totalSteps = 13; // Based on ProcessStep enum
        const completedSteps = this.processSteps.filter(s => s.status === 'completed').length;
        const progress = (completedSteps / totalSteps) * 100;
        
        const progressFill = document.getElementById('progress-fill');
        progressFill.style.width = `${progress}%`;
    }
    
    handleInterventionRequest(interventionData) {
        const panel = document.getElementById('intervention-panel');
        const content = document.getElementById('intervention-content');
        
        content.innerHTML = `
            <p><strong>Step:</strong> ${interventionData.context.step}</p>
            <p><strong>Context:</strong> ${interventionData.context.explanation}</p>
            <div class="intervention-options">
                <button class="btn-intervention" onclick="this.respondToIntervention('approve')">
                    ✓ Approve
                </button>
                <button class="btn-intervention" onclick="this.respondToIntervention('modify')">
                    ✏️ Modify
                </button>
                <button class="btn-intervention" onclick="this.respondToIntervention('skip')">
                    ⏭️ Skip
                </button>
            </div>
        `;
        
        panel.style.display = 'block';
        panel.scrollIntoView({ behavior: 'smooth' });
        
        // Store intervention ID for response
        this.currentInterventionId = interventionData.intervention_id;
    }
    
    respondToIntervention(response) {
        if (!this.currentInterventionId) return;
        
        const responseMessage = {
            type: 'intervention_response',
            intervention_id: this.currentInterventionId,
            response: response,
            session_id: this.sessionId
        };
        
        this.websocket.send(JSON.stringify(responseMessage));
        
        // Hide intervention panel
        document.getElementById('intervention-panel').style.display = 'none';
        this.currentInterventionId = null;
    }
    
    displayResults(results) {
        const resultsSection = document.getElementById('results-section');
        const resultsContent = document.getElementById('results-content');
        
        resultsContent.innerHTML = `
            <div class="score-grid">
                <div class="score-card">
                    <div class="score-value">${Math.round(results.overall_score * 100)}%</div>
                    <div class="score-label">Overall Match</div>
                </div>
                <div class="score-card">
                    <div class="score-value">${Math.round(results.skills_match * 100)}%</div>
                    <div class="score-label">Skills Match</div>
                </div>
                <div class="score-card">
                    <div class="score-value">${Math.round(results.experience_match * 100)}%</div>
                    <div class="score-label">Experience Match</div>
                </div>
                <div class="score-card">
                    <div class="score-value">${Math.round((results.detailed_analysis.seo_sem_score || 0) * 100)}%</div>
                    <div class="score-label">SEO/SEM</div>
                </div>
                <div class="score-card">
                    <div class="score-value">${Math.round((results.detailed_analysis.martech_score || 0) * 100)}%</div>
                    <div class="score-label">MarTech</div>
                </div>
                <div class="score-card">
                    <div class="score-value">${Math.round((results.detailed_analysis.advanced_analytics_score || 0) * 100)}%</div>
                    <div class="score-label">Analytics</div>
                </div>
            </div>
            
            ${results.candidate_name ? `
                <div style="margin-top: 20px;">
                    <h4>Candidate: ${results.candidate_name}</h4>
                    ${results.candidate_email ? `<p>Email: ${results.candidate_email}</p>` : ''}
                </div>
            ` : ''}
            
            ${results.recommendations && results.recommendations.length > 0 ? `
                <div style="margin-top: 20px;">
                    <h4>Interview Recommendations:</h4>
                    <ul>
                        ${results.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
        
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    clearTimeline() {
        document.getElementById('process-timeline').innerHTML = '';
        document.getElementById('progress-fill').style.width = '0%';
    }
    
    hideResults() {
        document.getElementById('results-section').style.display = 'none';
        document.getElementById('intervention-panel').style.display = 'none';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add container if it doesn't exist
    if (!document.getElementById('cv-analyzer-container')) {
        const container = document.createElement('div');
        container.id = 'cv-analyzer-container';
        document.body.appendChild(container);
    }
    
    // Initialize the analyzer
    window.cvAnalyzer = new RealtimeCVAnalyzer();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RealtimeCVAnalyzer;
}