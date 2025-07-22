# 🚀 AWS Lightsail Deployment Guide

## Quick Setup (5 minutes)

### Step 1: Create Lightsail Instance
1. Go to [AWS Lightsail Console](https://lightsail.aws.amazon.com/)
2. Click "Create instance"
3. Choose:
   - **Platform**: Linux/Unix
   - **Blueprint**: Ubuntu 22.04 LTS
   - **Instance plan**: $3.50/month (1 vCPU, 512 MB RAM, 20 GB SSD)
   - **Instance name**: `cv-screener-production`
4. Click "Create instance"

### Step 2: Connect and Deploy
1. Wait for instance to be "Running" (about 2 minutes)
2. Click "Connect using SSH" in the Lightsail console
3. Run the deployment script:

```bash
# Download and run the deployment script
curl -O https://raw.githubusercontent.com/StreetsDigital/cv_mvp/main/deploy-lightsail.sh
chmod +x deploy-lightsail.sh
./deploy-lightsail.sh
```

### Step 3: Add Your API Key
```bash
# Edit the environment file
nano /opt/cv_mvp/.env

# Add your Anthropic API key:
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Restart the service
sudo systemctl restart cv-screener
```

### Step 4: Access Your App
- Your app will be running at: `http://YOUR_LIGHTSAIL_IP`
- Health check: `http://YOUR_LIGHTSAIL_IP/health`

## Optional: Custom Domain Setup

### In Lightsail Console:
1. Go to "Networking" tab
2. Click "Create static IP"
3. Attach it to your instance
4. Set up DNS zone for your domain
5. Create A record pointing to your static IP

### Enable HTTPS (free):
```bash
# Install Certbot
sudo snap install --classic certbot

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is set up automatically
```

## Monitoring & Maintenance

### Check Status:
```bash
sudo systemctl status cv-screener
sudo systemctl status nginx
```

### View Logs:
```bash
# Application logs
sudo journalctl -u cv-screener -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Update Application:
```bash
cd /opt/cv_mvp
sudo git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart cv-screener
```

## Cost Breakdown
- **Lightsail Instance**: $3.50/month
- **Data Transfer**: 1 TB included
- **Static IP**: Free (if attached)
- **DNS Zone**: $0.50/month (optional)

**Total**: ~$3.50/month for reliable hosting! 🎉