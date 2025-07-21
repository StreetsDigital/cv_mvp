# Enhanced CV Screening with Real-Time Process Visualization

## Overview
This project combines the complete CV automation workflow from the original implementation with enhanced real-time process visualization and transparency features. It provides clients with step-by-step AI reasoning, human-in-the-loop controls, and a unified interface for CV screening.

## Key Features
- **Real-time Process Explanation**: See exactly what the AI is doing step-by-step
- **Human-in-the-Loop Controls**: Intervene and guide the AI process when needed
- **Single Unified Interface**: No toggle between chat/analysis modes
- **Enhanced Transparency**: Confidence scores, reasoning explanations, and decision logic
- **Claude Code Integration**: Optimized for Claude Code development workflow

## Project Structure
```
enhanced-cv-screening-v1.1/
├── backend/                    # Core backend services
│   ├── models/                # Enhanced Pydantic models
│   ├── processors/            # CV processing engines
│   ├── analyzers/             # Skill detection & scoring
│   ├── explainers/            # NEW: Process explanation engine
│   ├── services/              # Core services (CV, vector, email, etc.)
│   ├── workflows/             # Workflow orchestration
│   └── utils/                 # Utilities and helpers
├── frontend/                   # React/TypeScript frontend
│   ├── components/            # Reusable components
│   ├── chat-interface/        # Real-time process visualization
│   └── ui-layouts/            # Single-interface layouts
├── slack_app/                  # Slack integration
│   ├── handlers/              # Message and interaction handlers
│   └── blocks/                # UI block definitions
├── integration/                # Claude Code integration
│   ├── claude-code/           # Claude Code specific implementations
│   └── deployment/            # Deployment configurations
└── tests/                      # Test suites
```

## Quick Start with Claude Code

### 1. Initialize the project
```bash
claude-code create-project enhanced-cv-screening --template=fastapi-react
cd enhanced-cv-screening-v1.1
```

### 2. Set up environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
npm install  # for frontend
```

### 4. Run the application
```bash
# Backend
uvicorn backend.main:app --reload

# Frontend (separate terminal)
npm start

# Slack app (separate terminal)  
python -m slack_app.app
```

## Key Enhancements in V1.1

### 1. Real-Time Process Visualization
- WebSocket-based real-time updates
- Step-by-step AI reasoning explanation
- Confidence scores for all detections
- Visual progress indicators

### 2. Human-in-the-Loop Features
- Intervention points throughout the process
- Keyword priority management
- Scoring weight adjustments
- Review and approval workflows

### 3. Enhanced Transparency
- Detailed scoring explanations
- Pattern matching visibility
- Industry expertise analysis
- Recommendation reasoning

### 4. Single Unified Interface
- Integrated process chat window
- No separate analysis/chat modes
- Real-time updates in main interface
- Streamlined user experience

## Technologies Used
- **Backend**: FastAPI, Pydantic, WebSocket
- **AI Integration**: Anthropic Claude API
- **Vector Database**: Pinecone
- **Frontend**: React, TypeScript, WebSocket hooks
- **Communication**: Slack Bolt Python
- **Deployment**: Docker, Docker Compose

## Documentation
- [API Documentation](docs/api.md)
- [Frontend Components](docs/frontend.md)
- [Process Flow Specification](docs/process-flow.md)
- [Claude Code Integration Guide](docs/claude-code.md)
- [Deployment Guide](docs/deployment.md)

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License
MIT License - see LICENSE file for details
