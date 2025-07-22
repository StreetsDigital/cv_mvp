# 📚 Complete AWS Setup & Deployment Guide

This guide will walk you through every step from AWS account creation to deployed API.

## 📋 Table of Contents
1. [AWS Account Setup](#1-aws-account-setup)
2. [Create IAM User](#2-create-iam-user)
3. [Install Required Tools](#3-install-required-tools)
4. [Configure AWS Credentials](#4-configure-aws-credentials)
5. [Deploy Your API](#5-deploy-your-api)
6. [Test Your Deployment](#6-test-your-deployment)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. AWS Account Setup

### Create AWS Account (if you don't have one)
1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Enter your email and choose a password
4. Select "Personal" account type
5. Enter payment information (required, but we'll use free tier)
6. Verify your phone number
7. Choose "Basic Plan" (free)

### Sign into AWS Console
1. Go to https://console.aws.amazon.com/
2. Sign in with your email and password
3. You'll see the AWS Management Console

---

## 2. Create IAM User

We need to create a programmatic user for deployments.

### Step-by-Step IAM Setup:

1. **Navigate to IAM**
   - In AWS Console, search for "IAM" in the top search bar
   - Click on "IAM" (Identity and Access Management)

2. **Create User**
   - Click "Users" in the left sidebar
   - Click "Add users" button
   - User name: `cv-screening-deployer`
   - Select "Access key - Programmatic access" ✓
   - Click "Next: Permissions"

3. **Set Permissions**
   - Select "Attach existing policies directly"
   - Search and check these policies:
     - ✓ `AWSLambdaFullAccess`
     - ✓ `AmazonAPIGatewayAdministrator`
     - ✓ `AWSCloudFormationFullAccess`
     - ✓ `IAMFullAccess`
     - ✓ `AmazonS3FullAccess`
   - Click "Next: Tags" → "Next: Review" → "Create user"

4. **Save Credentials** ⚠️ IMPORTANT
   - You'll see "Access key ID" and "Secret access key"
   - Click "Show" next to Secret access key
   - **SAVE THESE NOW** - you won't see the secret again!
   - Copy both values to a secure location

Example credentials (yours will be different):
```
Access key ID: AKIAIOSFODNN7EXAMPLE
Secret access key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

---

## 3. Install Required Tools

### For macOS:
```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js
brew install node

# Install AWS CLI
brew install awscli

# Install Serverless Framework
npm install -g serverless
```

### For Windows:
1. **Install Node.js**
   - Download from https://nodejs.org/
   - Run installer, keep defaults

2. **Install AWS CLI**
   - Download from https://aws.amazon.com/cli/
   - Run MSI installer

3. **Install Serverless** (in Command Prompt/PowerShell)
   ```bash
   npm install -g serverless
   ```

### For Linux:
```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install AWS CLI
sudo apt-get install awscli

# Install Serverless
sudo npm install -g serverless
```

### Verify Installation:
```bash
node --version      # Should show v16+ or v18+
aws --version       # Should show aws-cli version
serverless --version # Should show Framework Core: 3.x.x
```

---

## 4. Configure AWS Credentials

### Option A: Using AWS CLI (Recommended)
```bash
aws configure
```

You'll be prompted for:
```
AWS Access Key ID [None]: YOUR_ACCESS_KEY_ID
AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
Default region name [None]: us-east-1
Default output format [None]: json
```

### Option B: Using Environment Variables
```bash
# For macOS/Linux - add to ~/.bashrc or ~/.zshrc
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY"
export AWS_DEFAULT_REGION="us-east-1"

# For Windows (Command Prompt)
set AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
set AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY
set AWS_DEFAULT_REGION=us-east-1

# For Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"
$env:AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY"
$env:AWS_DEFAULT_REGION="us-east-1"
```

### Set Anthropic API Key:
```bash
# macOS/Linux
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Windows Command Prompt
set ANTHROPIC_API_KEY=your-anthropic-api-key

# Windows PowerShell
$env:ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### Verify Credentials:
```bash
aws sts get-caller-identity
```

Should return:
```json
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/cv-screening-deployer"
}
```

---

## 5. Deploy Your API

### Prepare for Deployment:

1. **Navigate to project directory**
   ```bash
   cd "/Users/streetsdigital/Documents/Projects/Pydantic flow - CV Screener"
   ```

2. **Install Node dependencies**
   ```bash
   npm install
   ```

3. **Run deployment test** (optional but recommended)
   ```bash
   python3 test_aws_deployment.py
   ```

### Deploy to AWS:

**Option 1: Using deployment script**
```bash
./deploy-aws.sh
```

**Option 2: Direct Serverless command**
```bash
serverless deploy --verbose
```

### What Happens During Deployment:

You'll see output like:
```
Deploying cv-screening-api to stage prod (us-east-1)

Creating Stack...
✓ Stack create finished...

Uploading artifacts...
✓ Uploading service cv-screening-api.zip file (15 MB)...

Updating Stack...
✓ Stack update finished...

Service Information
service: cv-screening-api
stage: prod
region: us-east-1
stack: cv-screening-api-prod
endpoints:
  ANY - https://abc123def4.execute-api.us-east-1.amazonaws.com/prod/{proxy+}
  ANY - https://abc123def4.execute-api.us-east-1.amazonaws.com/prod/
functions:
  api: cv-screening-api-prod-api
```

**SAVE YOUR API URL!** It's the endpoint that starts with `https://`

---

## 6. Test Your Deployment

### Test 1: Health Check
```bash
# Replace with your actual API URL
curl https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/health
```

Expected response:
```json
{"status": "healthy", "version": "1.0.0"}
```

### Test 2: API Configuration
```bash
curl https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/api/config
```

### Test 3: CV Analysis
```bash
curl -X POST https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "John Smith, Software Engineer with 5 years Python experience",
    "job_description": "Looking for Senior Python Developer"
  }'
```

### Test 4: Web Interface
Open in browser:
```
https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/frontend/realtime-demo.html
```

---

## 7. Troubleshooting

### Common Issues & Solutions:

**"Serverless command not found"**
```bash
# Reinstall globally
npm install -g serverless
# Or use npx
npx serverless deploy
```

**"AWS credentials not configured"**
```bash
# Check credentials
aws configure list
# Reconfigure if needed
aws configure
```

**"Deployment failed - CloudFormation error"**
1. Go to AWS Console → CloudFormation
2. Find your stack (cv-screening-api-prod)
3. Click "Events" tab to see error details

**"API returns 502 Bad Gateway"**
```bash
# Check Lambda logs
serverless logs -f api -t
# Usually means Lambda function error
```

**"Access Denied" errors**
- Verify IAM user has all required permissions
- Check AWS region matches your configuration

### Useful Commands:

```bash
# View deployment info
serverless info

# Stream logs in real-time
serverless logs -f api -t

# Remove deployment (careful!)
serverless remove

# Redeploy after changes
serverless deploy

# Deploy single function (faster)
serverless deploy -f api
```

---

## 🎉 Success Checklist

- [ ] AWS Account created
- [ ] IAM user created with permissions
- [ ] Access keys saved securely
- [ ] Tools installed (Node, AWS CLI, Serverless)
- [ ] AWS credentials configured
- [ ] Anthropic API key set
- [ ] Deployment successful
- [ ] Health check returns 200 OK
- [ ] API analysis endpoint works

---

## 📊 What's Next?

1. **Monitor Usage**
   - AWS Console → Lambda → Monitor tab
   - CloudWatch Logs for debugging

2. **Update Frontend**
   - Update API URL in your frontend code
   - Test all features end-to-end

3. **Set Budget Alert** (optional)
   - AWS Console → Billing → Budgets
   - Set alert at $5/month

4. **Custom Domain** (optional)
   - Route 53 or external DNS
   - API Gateway custom domains

---

## 💰 Cost Expectations

With AWS Free Tier:
- **First 1 million requests/month**: FREE
- **First 400,000 GB-seconds compute**: FREE
- **Typical monthly cost**: $0-5 for moderate usage

---

## 🆘 Need More Help?

1. **AWS Support**: https://aws.amazon.com/support/
2. **Serverless Docs**: https://www.serverless.com/framework/docs/
3. **Check logs**: `serverless logs -f api`
4. **GitHub Issues**: Report bugs in your repository

---

**🎯 Your API is now live on AWS Lambda with auto-scaling and enterprise-grade infrastructure!**