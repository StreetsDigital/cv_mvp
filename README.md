# 🎯 Enhanced CV Screening API v1.1

> AI-powered CV analysis with real-time processing, advanced scoring, and comprehensive candidate assessment.

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/StreetsDigital/cv_mvp.git
cd cv_mvp

# 2. Set environment variables
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# 3. Deploy to AWS (recommended)
cd deployment/aws
./deploy-with-aws-cli.sh

# 4. Test your deployment
curl https://your-api-url.amazonaws.com/prod/health
```

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Deployment Options](#deployment-options)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Documentation](#documentation)

## ✨ Features

### Core Functionality
- 🧠 **AI-Powered CV Analysis** using Claude AI
- 📊 **Advanced Scoring Engine** with 11 specialized metrics
- 📄 **Multi-Format Support** (PDF, DOCX, TXT)
- 🎯 **Job Matching** with detailed compatibility analysis
- 🔄 **Real-time Processing** with WebSocket updates
- 🛡️ **Enterprise Security** with rate limiting and CORS

### Advanced Features
- 📈 **Enhanced Skill Categories**: SEO/SEM, MarTech, Analytics, Platform Leadership
- 🎨 **Digital Media Expertise** assessment
- 👥 **Executive Readiness** evaluation
- 🌐 **Remote Work Capability** scoring
- 🏢 **Industry Specialization** analysis
- 💼 **Human-in-the-Loop** intervention controls

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │  Lambda/Server  │
│                 │───▶│                 │───▶│                 │
│ React/Vanilla   │    │  CORS Enabled   │    │   FastAPI App   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                               ┌─────────────────┐
                                               │   Claude AI     │
                                               │   Integration   │
                                               └─────────────────┘
```

### Tech Stack
- **Backend**: FastAPI, Pydantic, Python 3.9
- **AI**: Anthropic Claude API
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Deployment**: AWS Lambda, API Gateway, Vercel
- **Testing**: Pytest, asyncio testing

## 🚀 Deployment Options

### Option 1: AWS Lambda (Recommended)
```bash
cd deployment/aws
export ANTHROPIC_API_KEY="your-key"
./deploy-with-aws-cli.sh
```
- ✅ Auto-scaling
- ✅ Pay-per-request
- ✅ Enhanced CORS support
- ✅ Enterprise-grade security

### Option 2: Vercel Serverless
```bash
cd deployment/vercel
vercel deploy
```
- ✅ Quick deployment
- ✅ Global CDN
- ❌ Limited WebSocket support

### Option 3: Traditional Server
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

📖 **Detailed Guides**: See [`docs/deployment/`](docs/deployment/)

## 📚 API Documentation

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/config` | GET | App configuration |
| `/api/analyze` | POST | Standard CV analysis |
| `/api/analyze-enhanced` | POST | Enhanced CV analysis |
| `/api/upload` | POST | File upload |

### Example Usage

```javascript
// Analyze CV
const response = await fetch('/api/analyze-enhanced', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    cv_text: "John Smith, Software Engineer...",
    job_description: "Senior Python Developer..."
  })
});

const analysis = await response.json();
console.log(analysis.overall_score); // 85.5
```

📖 **Full API Docs**: See [`docs/api/`](docs/api/)

## 🛠️ Development

### Local Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-key"
export DEBUG=true

# Run development server
uvicorn app.main:app --reload
```

### Project Structure
```
cv-screening-api/
├── app/                     # Main application
│   ├── main.py             # FastAPI app
│   ├── config.py           # Configuration
│   ├── models/             # Pydantic models
│   ├── services/           # Business logic
│   ├── middleware/         # Custom middleware
│   └── utils/              # Utilities
├── frontend/               # Web interface
├── tests/                  # Test suite
├── deployment/             # Deployment configs
├── docs/                   # Documentation
└── scripts/               # Utility scripts
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Test specific component
python -m pytest tests/test_cv_processor.py

# Integration tests
python scripts/test_production_ready.py
```

## 📖 Documentation

### Quick Links
- 🚀 [AWS Deployment Guide](docs/deployment/AWS_COMPLETE_SETUP_GUIDE.md)
- 🔧 [CORS Troubleshooting](docs/troubleshooting/CORS_TROUBLESHOOTING_GUIDE.md)
- 📊 [API Implementation](docs/api/ENHANCED_IMPLEMENTATION_GUIDE.md)
- 🐛 [Troubleshooting](docs/troubleshooting/)

### Documentation Structure
```
docs/
├── deployment/          # Deployment guides
│   ├── AWS_COMPLETE_SETUP_GUIDE.md
│   ├── SECURE_AWS_DEPLOYMENT.md
│   └── VERCEL_DEPLOYMENT_GUIDE.md
├── api/                # API documentation
│   ├── ENHANCED_IMPLEMENTATION_GUIDE.md
│   └── V11_IMPLEMENTATION_SUMMARY.md
└── troubleshooting/    # Guides and FAQs
    └── CORS_TROUBLESHOOTING_GUIDE.md
```

## 🔒 Security

- ✅ **Input Validation**: Pydantic models
- ✅ **Rate Limiting**: Configurable limits
- ✅ **CORS Protection**: Multi-layer CORS handling
- ✅ **Secret Management**: Environment variables
- ✅ **Error Handling**: Secure error responses

## 💰 Cost Estimate

### AWS Lambda (Recommended)
- **Free Tier**: 1M requests/month FREE
- **After Free Tier**: ~$0.20 per 1M requests
- **Typical Usage**: $1-5/month

### Vercel
- **Hobby Plan**: FREE for personal projects
- **Pro Plan**: $20/month for commercial use

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 **Issues**: [GitHub Issues](https://github.com/StreetsDigital/cv_mvp/issues)
- 📖 **Documentation**: [docs/](docs/)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/StreetsDigital/cv_mvp/discussions)

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration with ATS systems
- [ ] Mobile application
- [ ] Batch processing capabilities

---

**🚀 Built with [Claude Code](https://claude.ai/code) - AI-powered development**

*Transform your recruitment process with AI-driven CV analysis and real-time insights.*