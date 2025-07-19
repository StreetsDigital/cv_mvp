// CV Automation Frontend Application
class CVAutomationApp {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.currentView = 'both'; // 'both', 'chat', 'form'
        this.apiBase = window.location.origin;
        this.init();
    }

    generateSessionId() {
        return 'sess_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }

    init() {
        this.initEventListeners();
        this.initFileUpload();
        this.initChat();
        this.loadAppConfig();
    }

    // Event Listeners
    initEventListeners() {
        // Header buttons
        document.getElementById('toggleView').addEventListener('click', () => this.toggleView());
        document.getElementById('clearChat').addEventListener('click', () => this.clearChat());
        document.getElementById('newAnalysis').addEventListener('click', () => this.newAnalysis());

        // Form submission
        document.getElementById('analyzeButton').addEventListener('click', () => this.analyzeCV());

        // Form validation
        document.getElementById('cvTextInput').addEventListener('input', () => this.validateForm());
        document.getElementById('jobDescInput').addEventListener('input', () => this.validateForm());

        // Modal controls
        document.getElementById('closeUpgradeModal').addEventListener('click', () => this.closeModal());

        // Quick commands
        document.querySelectorAll('.quick-command').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const command = e.currentTarget.dataset.command;
                this.executeQuickCommand(command);
            });
        });

        // Chat input
        const chatInput = document.getElementById('chatInput');
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendChatMessage();
            }
        });
        chatInput.addEventListener('input', () => this.validateChatInput());

        // Send button
        document.getElementById('sendBtn').addEventListener('click', () => this.sendChatMessage());

        // Attach button
        document.getElementById('attachBtn').addEventListener('click', () => {
            document.getElementById('chatFileInput').click();
        });

        // Chat file input
        document.getElementById('chatFileInput').addEventListener('change', (e) => {
            this.handleChatFileUpload(e.target.files[0]);
        });
    }

    // File Upload Functionality
    initFileUpload() {
        const uploadArea = document.getElementById('cvUploadArea');
        const fileInput = document.getElementById('cvFile');

        // Click to upload
        uploadArea.addEventListener('click', () => fileInput.click());

        // File input change
        fileInput.addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files[0]);
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });
    }

    // Chat Functionality
    initChat() {
        this.messagesContainer = document.getElementById('messagesContainer');
        this.addWelcomeMessage();
    }

    addWelcomeMessage() {
        // Welcome message is already in HTML
    }

    // API Methods
    async loadAppConfig() {
        try {
            const response = await fetch(`${this.apiBase}/api/config`);
            if (response.ok) {
                this.config = await response.json();
            }
        } catch (error) {
            console.error('Failed to load app config:', error);
        }
    }

    async handleFileUpload(file) {
        if (!file) return;

        try {
            this.showLoading(true);
            
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${this.apiBase}/api/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                document.getElementById('cvTextInput').value = result.file_content;
                this.validateForm();
                this.showNotification('File uploaded successfully!', 'success');
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            console.error('File upload error:', error);
            this.showNotification('Error uploading file', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async handleChatFileUpload(file) {
        if (!file) return;

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${this.apiBase}/api/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                // Send file content as chat message
                await this.sendChatMessage({
                    content: result.file_content,
                    message_type: 'file',
                    file_name: file.name,
                    file_type: file.type
                });
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            console.error('Chat file upload error:', error);
            this.showNotification('Error uploading file', 'error');
        }
    }

    async analyzeCV() {
        const cvText = document.getElementById('cvTextInput').value.trim();
        const jobDesc = document.getElementById('jobDescInput').value.trim();

        if (!cvText || !jobDesc) {
            this.showNotification('Please provide both CV and job description', 'error');
            return;
        }

        try {
            this.showLoading(true);
            this.setAnalyzeButtonLoading(true);

            const response = await fetch(`${this.apiBase}/api/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cv_text: cvText,
                    job_description: jobDesc
                })
            });

            if (response.status === 429) {
                const rateLimitData = await response.json();
                this.showRateLimitModal(rateLimitData);
                return;
            }

            const result = await response.json();

            if (result.success) {
                this.displayAnalysisResults(result);
                this.trackAction();
            } else {
                this.showNotification('Analysis failed', 'error');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.showNotification('Error performing analysis', 'error');
        } finally {
            this.showLoading(false);
            this.setAnalyzeButtonLoading(false);
        }
    }

    async sendChatMessage(messageData = null) {
        const chatInput = document.getElementById('chatInput');
        const message = messageData || {
            content: chatInput.value.trim(),
            message_type: 'text'
        };

        if (!message.content) return;

        try {
            // Add user message to chat
            if (!messageData) {
                this.addMessageToChat('user', message.content);
                chatInput.value = '';
                this.validateChatInput();
            }

            // Show typing indicator
            this.showTypingIndicator();

            const response = await fetch(`${this.apiBase}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ...message,
                    session_id: this.sessionId
                })
            });

            if (response.status === 429) {
                const rateLimitData = await response.json();
                this.hideTypingIndicator();
                this.showRateLimitModal(rateLimitData);
                return;
            }

            const result = await response.json();
            this.hideTypingIndicator();

            // Add assistant response
            this.addMessageToChat('assistant', result.content);

            // Handle modal triggers
            if (result.metadata?.show_modal) {
                setTimeout(() => this.showUpgradeModal(result.metadata.modal_data), 1000);
            }

            this.trackAction();
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTypingIndicator();
            this.addMessageToChat('system', 'Sorry, I encountered an error. Please try again.');
        }
    }

    async trackAction() {
        try {
            const response = await fetch(`${this.apiBase}/api/track-action`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });

            const result = await response.json();

            if (result.show_modal && result.modal_data) {
                setTimeout(() => this.showUpgradeModal(result.modal_data), 2000);
            }
        } catch (error) {
            console.error('Action tracking error:', error);
        }
    }

    // UI Methods
    toggleView() {
        const toggleBtn = document.getElementById('toggleView');
        const quickForm = document.getElementById('quickForm');
        const chatInterface = document.getElementById('chatInterface');

        if (this.currentView === 'both') {
            // Switch to chat only
            quickForm.style.display = 'none';
            chatInterface.style.flex = '1';
            toggleBtn.innerHTML = '<i class="fas fa-columns"></i> <span>Show Both</span>';
            this.currentView = 'chat';
        } else {
            // Switch back to both
            quickForm.style.display = 'block';
            chatInterface.style.flex = '1';
            toggleBtn.innerHTML = '<i class="fas fa-comments"></i> <span>Chat Only</span>';
            this.currentView = 'both';
        }
    }

    clearChat() {
        const messagesContainer = document.getElementById('messagesContainer');
        messagesContainer.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-content">
                    <h3>
                        <i class="fas fa-comments"></i>
                        Chat-Based Analysis
                    </h3>
                    <p>Prefer a guided, conversational approach? Start chatting below.</p>
                    <div class="quick-commands">
                        <button class="quick-command" data-command="help">
                            <i class="fas fa-question-circle"></i> Help
                        </button>
                        <button class="quick-command" data-command="upload cv">
                            <i class="fas fa-upload"></i> Upload CV
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Re-attach event listeners for quick commands
        document.querySelectorAll('.quick-command').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const command = e.currentTarget.dataset.command;
                this.executeQuickCommand(command);
            });
        });
        
        this.sessionId = this.generateSessionId();
    }

    newAnalysis() {
        document.getElementById('cvTextInput').value = '';
        document.getElementById('jobDescInput').value = '';
        document.getElementById('resultsPreview').style.display = 'none';
        this.validateForm();
    }

    validateForm() {
        const cvText = document.getElementById('cvTextInput').value.trim();
        const jobDesc = document.getElementById('jobDescInput').value.trim();
        const analyzeBtn = document.getElementById('analyzeButton');

        analyzeBtn.disabled = !cvText || !jobDesc;
    }

    validateChatInput() {
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');

        sendBtn.disabled = !chatInput.value.trim();
    }

    setAnalyzeButtonLoading(loading) {
        const analyzeBtn = document.getElementById('analyzeButton');
        const span = analyzeBtn.querySelector('span');

        if (loading) {
            analyzeBtn.classList.add('loading');
            span.textContent = 'Analyzing...';
            analyzeBtn.disabled = true;
        } else {
            analyzeBtn.classList.remove('loading');
            span.textContent = 'Analyze CV Match';
            this.validateForm();
        }
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    displayAnalysisResults(result) {
        const resultsPreview = document.getElementById('resultsPreview');
        const scoreCircle = document.getElementById('scoreCircle');
        const scoreValue = document.getElementById('scoreValue');
        const candidateName = document.getElementById('candidateName').querySelector('span');
        const recommendation = document.getElementById('recommendation');
        const analysisDetails = document.getElementById('analysisDetails');

        // Set score and styling
        scoreValue.textContent = Math.round(result.overall_score);
        scoreCircle.className = 'score-circle';
        
        if (result.overall_score >= 70) {
            scoreCircle.classList.add('score-excellent');
        } else if (result.overall_score >= 50) {
            scoreCircle.classList.add('score-good');
        } else {
            scoreCircle.classList.add('score-poor');
        }

        // Set candidate info
        candidateName.textContent = result.candidate_name;
        recommendation.textContent = result.recommendation;

        // Build analysis details
        const analysis = result.analysis;
        analysisDetails.innerHTML = `
            <div class="detail-section">
                <h4>Skills Analysis</h4>
                <p><strong>Score:</strong> ${analysis.skills_match.score.toFixed(1)}/100</p>
                <p><strong>Matched Skills:</strong> ${analysis.skills_match.matched_skills.join(', ') || 'None'}</p>
                <p><strong>Missing Skills:</strong> ${analysis.skills_match.missing_skills.join(', ') || 'None'}</p>
            </div>
            <div class="detail-section">
                <h4>Experience Analysis</h4>
                <p><strong>Score:</strong> ${analysis.experience_match.score.toFixed(1)}/100</p>
                <p><strong>Candidate Experience:</strong> ${analysis.experience_match.candidate_years} years</p>
                <p><strong>Required Experience:</strong> ${analysis.experience_match.required_years} years</p>
            </div>
            <div class="detail-section">
                <h4>Education Analysis</h4>
                <p><strong>Score:</strong> ${analysis.education_match.score.toFixed(1)}/100</p>
                <p><strong>Candidate Education:</strong> ${analysis.education_match.candidate_education.join(', ') || 'Not specified'}</p>
                <p><strong>Required Education:</strong> ${analysis.education_match.required_education.join(', ') || 'Not specified'}</p>
            </div>
        `;

        resultsPreview.style.display = 'block';
        resultsPreview.scrollIntoView({ behavior: 'smooth' });
    }

    addMessageToChat(sender, content) {
        const messagesContainer = document.getElementById('messagesContainer');
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        let avatarIcon = '';
        if (sender === 'user') {
            avatarIcon = '<i class="fas fa-user"></i>';
        } else if (sender === 'assistant') {
            avatarIcon = '<i class="fas fa-robot"></i>';
        } else {
            avatarIcon = '<i class="fas fa-info-circle"></i>';
        }

        messageDiv.innerHTML = `
            <div class="message-avatar">${avatarIcon}</div>
            <div class="message-content">
                <div class="message-bubble">${this.formatMessageContent(content)}</div>
                <div class="message-time">${timestamp}</div>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    formatMessageContent(content) {
        // Convert markdown-like formatting to HTML
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message assistant typing-indicator';
        indicator.innerHTML = `
            <div class="message-avatar"><i class="fas fa-robot"></i></div>
            <div class="message-content">
                <div class="message-bubble">
                    <div class="typing-dots">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('messagesContainer').appendChild(indicator);
        document.getElementById('messagesContainer').scrollTop = document.getElementById('messagesContainer').scrollHeight;
    }

    hideTypingIndicator() {
        const indicator = document.querySelector('.typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    executeQuickCommand(command) {
        const chatInput = document.getElementById('chatInput');
        
        switch (command) {
            case 'help':
                chatInput.value = 'help';
                break;
            case 'upload cv':
                document.getElementById('chatFileInput').click();
                return;
            default:
                chatInput.value = command;
        }
        
        this.validateChatInput();
        this.sendChatMessage();
    }

    showUpgradeModal(modalData = null) {
        const modal = document.getElementById('upgradeModal');
        
        if (modalData) {
            // Update modal content with dynamic data
            const title = modal.querySelector('h2');
            const featuresList = modal.querySelector('.features-grid');
            
            if (modalData.title) {
                title.textContent = modalData.title;
            }
            
            if (modalData.features) {
                featuresList.innerHTML = modalData.features.map(feature => `
                    <div class="feature-card">
                        <div class="feature-icon">${feature.split(' ')[0]}</div>
                        <h4>${feature.substring(feature.indexOf(' ') + 1)}</h4>
                        <p>Enhanced functionality available in premium plan</p>
                    </div>
                `).join('');
            }
        }
        
        modal.style.display = 'flex';
    }

    showRateLimitModal(rateLimitData) {
        // Create and show rate limit modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <div class="upgrade-icon">🚫</div>
                    <h2>Rate Limit Reached</h2>
                    <p>You've reached your daily limit for the free tier</p>
                    <button class="close-button" onclick="this.closest('.modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <p>${rateLimitData.message}</p>
                    <div style="text-align: center; margin-top: 20px;">
                        <button class="cta-primary" onclick="window.open('mailto:${rateLimitData.contact_email}?subject=CV Automation - Upgrade Request', '_blank')">
                            <i class="fas fa-envelope"></i> Contact for Upgrade
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    closeModal() {
        document.getElementById('upgradeModal').style.display = 'none';
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        // Add notification styles if not already present
        if (!document.querySelector('#notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 3000;
                    max-width: 400px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                    animation: slideIn 0.3s ease;
                }
                .notification-success { border-left: 4px solid #10b981; }
                .notification-error { border-left: 4px solid #ef4444; }
                .notification-info { border-left: 4px solid #3b82f6; }
                .notification-content {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 16px;
                }
                .notification button {
                    background: none;
                    border: none;
                    font-size: 18px;
                    cursor: pointer;
                    color: #9ca3af;
                }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
}

// Add typing indicator styles
const typingStyles = document.createElement('style');
typingStyles.textContent = `
    .typing-dots {
        display: flex;
        gap: 4px;
        align-items: center;
    }
    .typing-dots span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #9ca3af;
        animation: typing 1.4s ease-in-out infinite;
    }
    .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
        30% { transform: translateY(-8px); opacity: 1; }
    }
`;
document.head.appendChild(typingStyles);

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cvApp = new CVAutomationApp();
});

// Handle modal close on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal[style*="flex"]');
        modals.forEach(modal => modal.style.display = 'none');
    }
});

// Handle modal close on backdrop click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});