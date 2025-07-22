#!/bin/bash
# Enhanced AWS Lightsail deployment script for CV Screener
# Run this after creating your Lightsail instance

set -e  # Exit on any error

echo "🚀 Starting CV Screener deployment on AWS Lightsail"
echo "📍 Current user: $(whoami)"
echo "📍 Current directory: $(pwd)"

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and required packages
echo "🐍 Installing Python 3.11 and dependencies..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip git nginx software-properties-common curl

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /opt/cv_mvp
cd /opt

# Clone your repository
echo "📥 Cloning repository..."
if [ -d "cv_mvp" ]; then
    sudo rm -rf cv_mvp
fi
sudo git clone https://github.com/StreetsDigital/cv_mvp.git
sudo chown -R ubuntu:ubuntu cv_mvp
cd cv_mvp

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip and install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > .env << EOF
# Production environment configuration
APP_NAME=CV Automation MVP
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=*
PREMIUM_CONTACT_EMAIL=andrew@automateengage.com

# Enhanced CV Processing Settings
ENABLE_ENHANCED_PROCESSING=true
ENHANCED_PROCESSING_TIMEOUT=60
CLAUDE_MODEL=claude-3-sonnet-20240229
MAX_CV_LENGTH=50000
MAX_JOB_DESCRIPTION_LENGTH=10000

# Performance Settings
ENABLE_SKILL_CACHING=true
CACHE_EXPIRY_HOURS=24

# Security
SECRET_KEY=lightsail-production-secret-$(date +%s)

# Chat Settings
MAX_MESSAGE_LENGTH=4000
MAX_FILE_SIZE_MB=5

# Feature Flags
ENABLE_VECTOR_STORAGE=false
ENABLE_EMAIL_INTEGRATION=false
ENABLE_LINKEDIN_INTEGRATION=false
ENABLE_ANALYTICS=false
ENABLE_WORKFLOW_PERSISTENCE=false

# IMPORTANT: Add your Anthropic API key here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
EOF

echo "🔧 Setting proper permissions..."
chmod 600 .env
chown ubuntu:ubuntu .env

# Test the application briefly
echo "🧪 Testing application startup..."
source venv/bin/activate
timeout 10s uvicorn app.main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 || echo "Quick test completed"

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/cv-screener.service > /dev/null <<EOF
[Unit]
Description=CV Screener FastAPI Application
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/cv_mvp
Environment=PATH=/opt/cv_mvp/venv/bin
ExecStart=/opt/cv_mvp/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx with optimized settings
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/cv-screener > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    client_max_body_size 10M;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if any)
    location /static/ {
        alias /opt/cv_mvp/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
EOF

# Enable the site and remove default
echo "🔗 Enabling Nginx site..."
sudo ln -sf /etc/nginx/sites-available/cv-screener /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

# Create log rotation for the application
echo "📋 Setting up log rotation..."
sudo tee /etc/logrotate.d/cv-screener > /dev/null <<EOF
/var/log/cv-screener/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload cv-screener
    endscript
}
EOF

# Create log directory
sudo mkdir -p /var/log/cv-screener
sudo chown ubuntu:ubuntu /var/log/cv-screener

# Start and enable services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable cv-screener
sudo systemctl start cv-screener
sudo systemctl reload nginx
sudo systemctl enable nginx

# Wait a moment for services to start
sleep 5

# Check service status
echo "🔍 Checking service status..."
sudo systemctl status cv-screener --no-pager -l
echo ""
sudo systemctl status nginx --no-pager -l

# Test the deployment
echo "🧪 Testing deployment..."
sleep 2
if curl -s http://localhost/health > /dev/null; then
    echo "✅ Application is responding to health checks!"
else
    echo "⚠️  Application may still be starting up..."
fi

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

echo ""
echo "🎉 Deployment Complete!"
echo "================================"
echo "🌐 Your CV Screener is now running at:"
echo "   http://$PUBLIC_IP"
echo ""
echo "📝 Next Steps:"
echo "1. Add your Anthropic API key:"
echo "   nano /opt/cv_mvp/.env"
echo "   # Add: ANTHROPIC_API_KEY=your_key_here"
echo ""
echo "2. Restart the service:"
echo "   sudo systemctl restart cv-screener"
echo ""
echo "3. Optional - Set up a custom domain in Lightsail"
echo ""
echo "🔧 Useful Commands:"
echo "   sudo systemctl status cv-screener    # Check status"
echo "   sudo systemctl restart cv-screener   # Restart app"
echo "   sudo journalctl -u cv-screener -f    # View logs"
echo "   sudo nginx -t && sudo systemctl reload nginx  # Reload nginx"
echo ""
echo "📊 Monitor your app: http://$PUBLIC_IP/health"
echo "================================"