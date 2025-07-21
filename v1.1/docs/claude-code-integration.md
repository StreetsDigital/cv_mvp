# Claude Code Integration Guide

## Overview
This project is optimized for Claude Code development workflow, providing seamless integration with Claude's coding capabilities for rapid development and deployment.

## Quick Start with Claude Code

### 1. Project Initialization
```bash
# Navigate to the project directory
cd /tmp/enhanced-cv-screening-v1.1

# Initialize Claude Code project
claude-code init --project-type=fastapi-react --name=enhanced-cv-screening

# Install dependencies
claude-code install-deps
```

### 2. Backend Setup
```bash
# Set up Python environment
claude-code setup-python --version=3.9
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Start backend development server
claude-code run-backend --port=8000
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
claude-code setup-node --version=18
npm install

# Start frontend development server
claude-code run-frontend --port=3000
```

## Claude Code Commands for This Project

### Development Commands
```bash
# Create new components
claude-code create-component ProcessMessage --type=react
claude-code create-component HumanInterventionPanel --type=react

# Add new backend services
claude-code create-service EnhancedCVProcessor --type=async-service
claude-code create-service WebSocketManager --type=websocket-service
```

### Testing Commands
```bash
# Run tests with Claude Code
claude-code test --type=unit --coverage
claude-code test --type=integration --websocket
```

### Deployment Commands
```bash
# Build for production
claude-code build --environment=production

# Deploy to development
claude-code deploy --environment=development --with-websocket
```

This integration guide ensures optimal development workflow with Claude Code.
