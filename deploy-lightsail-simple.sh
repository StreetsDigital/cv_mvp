#!/bin/bash
# Simple and robust AWS Lightsail deployment script for CV Screener
# Handles Ubuntu automatic updates and kernel upgrade prompts

echo "🚀 CV Screener - Simple Lightsail Deployment"
echo "=============================================="

# Function to handle apt locks
wait_and_fix_apt() {
    echo "🔧 Ensuring APT is ready..."
    
    # Wait for any automatic updates
    while sudo fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; do
        echo "   Waiting for automatic updates to finish..."
        sleep 10
    done
    
    # Configure to avoid interactive prompts
    export DEBIAN_FRONTEND=noninteractive
    export NEEDRESTART_MODE=a
    
    # Fix any broken packages
    sudo dpkg --configure -a
    echo "✅ APT ready"
}

# Wait for apt to be available
wait_and_fix_apt

# Skip interactive prompts and update
echo "📦 Updating system (non-interactive)..."
export DEBIAN_FRONTEND=noninteractive
sudo -E apt update
sudo -E apt upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"

# Install essential packages
echo "🐍 Installing Python and dependencies..."
sudo -E apt install -y python3.11 python3.11-venv python3-pip git nginx curl

# Create app directory
echo "📁 Setting up application..."
sudo mkdir -p /opt/cv_mvp
cd /opt

# Clone repository
echo "📥 Downloading your CV Screener code..."
if [ -d "cv_mvp" ]; then
    sudo rm -rf cv_mvp
fi
sudo git clone https://github.com/StreetsDigital/cv_mvp.git
sudo chown -R ubuntu:ubuntu cv_mvp
cd cv_mvp

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create basic config
echo "⚙️ Creating configuration..."
cat > .env << 'EOF'
APP_NAME=CV Automation MVP
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=*
PREMIUM_CONTACT_EMAIL=andrew@automateengage.com
ENABLE_ENHANCED_PROCESSING=true
CLAUDE_MODEL=claude-3-sonnet-20240229
MAX_FILE_SIZE_MB=5
MAX_MESSAGE_LENGTH=4000
SECRET_KEY=lightsail-prod-secret
ENABLE_VECTOR_STORAGE=false
ENABLE_EMAIL_INTEGRATION=false
ENABLE_LINKEDIN_INTEGRATION=false
ENABLE_ANALYTICS=false
ENABLE_WORKFLOW_PERSISTENCE=false

# ADD YOUR API KEY HERE:
# ANTHROPIC_API_KEY=your_key_here
EOF

chmod 600 .env

# Create systemd service
echo "⚙️ Setting up auto-start service..."
sudo tee /etc/systemd/system/cv-screener.service > /dev/null << 'EOF'
[Unit]
Description=CV Screener FastAPI App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/cv_mvp
Environment=PATH=/opt/cv_mvp/venv/bin
ExecStart=/opt/cv_mvp/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure nginx
echo "🌐 Setting up web server..."
sudo tee /etc/nginx/sites-available/cv-screener > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/cv-screener /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable cv-screener
sudo systemctl start cv-screener
sudo systemctl reload nginx

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "YOUR_IP")

# Wait and test
sleep 5
echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "========================"
echo ""
echo "🌐 Your CV Screener is running at:"
echo "   http://$PUBLIC_IP"
echo ""
echo "🔑 IMPORTANT - Add your API key:"
echo "   nano /opt/cv_mvp/.env"
echo "   # Add line: ANTHROPIC_API_KEY=your_key_here"
echo "   sudo systemctl restart cv-screener"
echo ""
echo "🔍 Check status:"
echo "   sudo systemctl status cv-screener"
echo ""
echo "📋 View logs:"
echo "   sudo journalctl -u cv-screener -f"
echo ""
echo "✅ Health check: http://$PUBLIC_IP/health"
echo "========================"

# Test if app is responding
if curl -s http://localhost/health > /dev/null 2>&1; then
    echo "✅ App is responding!"
else
    echo "⚠️  App may still be starting up - check logs if needed"
fi
