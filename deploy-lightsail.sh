#!/bin/bash
# AWS Lightsail deployment script for CV Screener

echo "🚀 Setting up CV Screener on AWS Lightsail"

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx

# Clone your repository
cd /opt
sudo git clone https://github.com/StreetsDigital/cv_mvp.git
sudo chown -R $USER:$USER cv_mvp
cd cv_mvp

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/cv-screener.service > /dev/null <<EOF
[Unit]
Description=CV Screener FastAPI App
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/cv_mvp
Environment=PATH=/opt/cv_mvp/venv/bin
ExecStart=/opt/cv_mvp/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
sudo tee /etc/nginx/sites-available/cv-screener > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/cv-screener /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Start services
sudo systemctl daemon-reload
sudo systemctl enable cv-screener
sudo systemctl start cv-screener
sudo systemctl reload nginx

echo "✅ CV Screener deployed! Your app is running on port 80"
echo "🔧 Remember to add your ANTHROPIC_API_KEY to the environment"