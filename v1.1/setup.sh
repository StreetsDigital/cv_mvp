#!/bin/bash
# Setup script for Enhanced CV Screening v1.1
# Claude Code Compatible

set -e

echo "🚀 Setting up Enhanced CV Screening v1.1..."

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Create virtual environment for Python
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment variables
echo "⚙️ Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "🔧 Please edit .env file with your API keys before running the application"
else
    echo "✅ .env file already exists"
fi

# Set up frontend
echo "⚛️ Setting up frontend..."
cd frontend
if command -v npm &> /dev/null; then
    npm install
    echo "✅ Frontend dependencies installed"
else
    echo "❌ npm not found. Please install Node.js and npm"
fi
cd ..

# Create necessary directories
echo "📁 Creating additional directories..."
mkdir -p logs
mkdir -p data
mkdir -p uploads

# Set up database (if using Docker)
echo "🐳 Setting up Docker environment..."
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose found"
    echo "Run 'docker-compose up -d db redis' to start database services"
else
    echo "⚠️ Docker Compose not found. Database setup skipped."
fi

# Create startup scripts
echo "📜 Creating startup scripts..."

cat > start_backend.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
EOF

cat > start_frontend.sh << 'EOF'
#!/bin/bash
cd frontend
npm start
EOF

cat > start_all.sh << 'EOF'
#!/bin/bash
echo "Starting Enhanced CV Screening v1.1..."

# Start backend in background
echo "🚀 Starting backend..."
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend in background
echo "⚛️ Starting frontend..."
cd frontend
npm start &
FRONTEND_PID=$!

echo "✅ Application started!"
echo "📊 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📡 WebSocket: ws://localhost:8000/ws/analysis/{session_id}"

# Wait for user input to stop
echo "Press any key to stop all services..."
read -n 1

# Kill processes
kill $BACKEND_PID $FRONTEND_PID
echo "🛑 Application stopped"
EOF

chmod +x start_backend.sh start_frontend.sh start_all.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Start database: docker-compose up -d db redis"
echo "3. Start application: ./start_all.sh"
echo ""
echo "🔧 Development commands:"
echo "• Backend only: ./start_backend.sh"
echo "• Frontend only: ./start_frontend.sh"
echo "• Full application: ./start_all.sh"
echo ""
echo "📚 Documentation:"
echo "• Claude Code Integration: docs/claude-code-integration.md"
echo "• API Documentation: http://localhost:8000/docs (after starting backend)"
echo ""
echo "🚀 Ready for Claude Code development!"
