# CV Automation - Recruitment Assistant

A powerful AI-driven CV analysis and recruitment automation tool built with FastAPI and Claude AI.

## Features

- **CV Analysis**: Upload and analyze CVs in PDF, DOCX, or TXT format
- **Job Matching**: Compare candidates against job requirements with detailed scoring
- **Chat Interface**: Conversational AI assistant for interactive CV analysis
- **Rate Limiting**: Built-in usage limits for free tier
- **Premium Features**: Email automation, LinkedIn integration (coming soon)

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd cv-automation-recruitment

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Required: ANTHROPIC_API_KEY
```

### 3. Run Locally

```bash
# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access the application
# http://localhost:8000
```

### 4. Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard:
# - ANTHROPIC_API_KEY
# - SECRET_KEY
```

## API Endpoints

- `GET /` - Main application interface
- `POST /api/chat` - Chat with AI assistant
- `POST /api/upload` - Upload CV files
- `POST /api/analyze` - Direct CV analysis
- `GET /api/config` - Application configuration
- `GET /health` - Health check

## Usage

### Quick Analysis
1. Upload a CV file or paste CV text
2. Paste job description
3. Click "Analyze CV Match"
4. Review detailed analysis and scoring

### Chat Interface
1. Use the chat interface for conversational analysis
2. Upload files directly in chat
3. Ask specific questions about candidates
4. Get detailed insights and recommendations

## Architecture

```
app/
├── main.py              # FastAPI application
├── config.py            # Settings and configuration
├── models/              # Pydantic data models
├── services/            # Business logic
├── middleware/          # Rate limiting, tracking
└── utils/              # File processing utilities

frontend/
├── index.html          # Main UI
├── css/styles.css      # Styling
└── js/app.js          # Frontend logic
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude AI API key | Yes |
| `SECRET_KEY` | Application secret key | No |
| `DEBUG` | Debug mode | No |
| `CORS_ORIGINS` | Allowed origins | No |
| `PREMIUM_CONTACT_EMAIL` | Contact for premium features | No |

## Development

### Code Structure
- **Models**: Pydantic models for data validation
- **Services**: Business logic for CV processing and AI chat
- **Middleware**: Rate limiting and action tracking
- **Frontend**: Vanilla JavaScript with modern CSS

### Adding Features
1. Define models in `app/models/`
2. Implement business logic in `app/services/`
3. Add API endpoints in `app/main.py`
4. Update frontend in `frontend/`

## License

MIT License - see LICENSE file for details.

## Support

For premium features and enterprise support, contact: andrew@automateengage.com