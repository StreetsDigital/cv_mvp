# 🔐 Secure AWS Deployment Guide

## ⚠️ First: Secure Your AWS Account

**CRITICAL**: The old credentials you shared have been compromised and must be deactivated immediately.

### Step 1: Deactivate Compromised Credentials
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to **IAM** → **Users** → **cv-screening-deployer**
3. Click **Security credentials** tab
4. Find access key `AKIA3RYC5367N2ELSE6B`
5. Click **Actions** → **Delete** (or Make inactive)

### Step 2: Create New Secure Credentials
1. In the same IAM user page, click **Create access key**
2. Select **Command Line Interface (CLI)**
3. Check the confirmation box
4. Click **Create access key**
5. **SECURELY SAVE** the new credentials (don't share them!)

---

## 🚀 Deployment Options

You now have **3 deployment methods** - choose the one you prefer:

### Option A: AWS CLI + SAM (Recommended)
### Option B: Serverless Framework  
### Option C: Manual AWS Console

---

## 📋 Option A: AWS CLI + SAM Deployment

### Prerequisites:
```bash
# Install AWS CLI (if not installed)
# macOS: brew install awscli
# Windows: Download from AWS website

# Install SAM CLI
# macOS: brew install aws-sam-cli
# Windows: Download from AWS website

# Verify installations
aws --version
sam --version
```

### Secure Credential Setup:
```bash
# Configure AWS CLI with your NEW credentials
aws configure

# You'll be prompted for:
# AWS Access Key ID: [Enter your NEW access key]
# AWS Secret Access Key: [Enter your NEW secret key]  
# Default region: us-east-1
# Default output format: json

# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### Deploy:
```bash
# Navigate to project directory
cd "/Users/streetsdigital/Documents/Projects/Pydantic flow - CV Screener"

# Deploy with one command
./deploy-with-aws-cli.sh
```

**Expected Output:**
```
🚀 Deploying Enhanced CV Screening API using AWS CLI & SAM...
✅ AWS Account: 123456789012, Region: us-east-1
ℹ️  Building application with SAM...
✅ Build completed successfully!
ℹ️  Deploying to AWS...
🎉 Deployment completed successfully!

📍 Your API is live at:
   https://abc123def4.execute-api.us-east-1.amazonaws.com/prod/

🧪 Test your deployment:
   curl https://abc123def4.execute-api.us-east-1.amazonaws.com/prod/health
```

---

## 📋 Option B: Serverless Framework

### Prerequisites:
```bash
# Install Node.js and Serverless
npm install -g serverless

# Install project dependencies
npm install
```

### Deploy:
```bash
# Set credentials as environment variables
export AWS_ACCESS_KEY_ID="your-new-access-key"
export AWS_SECRET_ACCESS_KEY="your-new-secret-key"  
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Deploy
./deploy-aws.sh
# or
serverless deploy --verbose
```

---

## 📋 Option C: Manual Console Deployment

### Create Lambda Function:
1. Go to **AWS Console** → **Lambda**
2. Click **Create function**
3. Choose **Author from scratch**
4. Function name: `cv-screening-api`
5. Runtime: `Python 3.9`
6. Create function

### Upload Code:
1. Create deployment package:
   ```bash
   # Install dependencies locally
   pip install -r requirements-aws.txt -t .
   
   # Create zip file
   zip -r cv-screening-api.zip . -x "*.git*" "node_modules/*" "tests/*"
   ```
2. In Lambda console, upload the zip file
3. Set handler to: `lambda_handler.handler`

### Configure Environment Variables:
- `ANTHROPIC_API_KEY`: your-anthropic-api-key
- `DEBUG`: false
- `LOG_LEVEL`: INFO

### Create API Gateway:
1. Go to **API Gateway** → **Create API**
2. Choose **REST API**
3. Create resource `{proxy+}`
4. Add method `ANY` with Lambda integration
5. Enable CORS
6. Deploy to stage `prod`

---

## 🧪 Testing Your Deployment

### Test 1: Health Check
```bash
curl https://YOUR-API-URL/health
# Expected: {"status": "healthy", "version": "1.0.0"}
```

### Test 2: CORS Test
```bash
curl -X OPTIONS https://YOUR-API-URL/api/health \
  -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: POST" \
  -v
# Should return CORS headers
```

### Test 3: CV Analysis
```bash
curl -X POST https://YOUR-API-URL/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "John Smith, Software Engineer",
    "job_description": "Python Developer"
  }'
```

### Test 4: Frontend Demo
Open in browser:
```
https://YOUR-API-URL/frontend/realtime-demo.html
```

---

## 🔍 Monitoring & Debugging

### View Logs:
```bash
# AWS CLI method
aws logs tail /aws/lambda/cv-screening-api --follow

# SAM method  
sam logs -n cv-screening-api --tail

# Serverless method
serverless logs -f api -t
```

### Check CloudFormation:
```bash
# View stack status
aws cloudformation describe-stacks --stack-name cv-screening-api

# View stack events
aws cloudformation describe-stack-events --stack-name cv-screening-api
```

---

## 💰 Cost Management

### Set Billing Alert:
1. Go to **AWS Console** → **Billing** → **Budgets**
2. Create budget for $5/month
3. Set email alerts at 80% and 100%

### Monitor Usage:
```bash
# Check Lambda invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=cv-screening-api \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

---

## 🗑️ Cleanup (When Done Testing)

### Remove Deployment:
```bash
# SAM method
aws cloudformation delete-stack --stack-name cv-screening-api

# Serverless method
serverless remove

# Manual: Delete via AWS Console
```

### Remove S3 Bucket:
```bash
# Empty and delete deployment bucket
aws s3 rm s3://cv-screening-deployments-ACCOUNT-REGION --recursive
aws s3 rb s3://cv-screening-deployments-ACCOUNT-REGION
```

---

## 🔐 Security Best Practices

### Credential Security:
- ✅ Never share AWS credentials in chat/email
- ✅ Use environment variables, not hardcoded values
- ✅ Rotate credentials regularly
- ✅ Use IAM roles in production
- ✅ Enable MFA on your AWS account

### API Security:
- ✅ CORS properly configured
- ✅ Rate limiting enabled
- ✅ Input validation with Pydantic
- ✅ No secrets logged
- ✅ HTTPS enforced

---

## 🆘 Troubleshooting

### Common Issues:

**"AccessDenied" errors:**
- Verify IAM permissions include Lambda, API Gateway, CloudFormation
- Check AWS region matches your configuration

**"Package too large" errors:**
- Use requirements-aws.txt (lightweight dependencies)
- Exclude unnecessary files in deployment

**CORS errors:**
- Our enhanced CORS configuration should prevent these
- Check browser dev tools for specific error messages

**API returns 502:**
- Check Lambda logs for Python import errors
- Verify handler path is correct: `lambda_handler.handler`

---

## ✅ Success Checklist

- [ ] Old compromised credentials deactivated
- [ ] New secure credentials created and configured
- [ ] Deployment method chosen and tools installed
- [ ] Environment variables set securely
- [ ] Deployment completed successfully
- [ ] Health check returns 200 OK
- [ ] CORS test passes
- [ ] CV analysis endpoint works
- [ ] Billing alerts configured
- [ ] Monitoring set up

---

## 🎯 Next Steps After Deployment

1. **Update Frontend**: Use your new API URL
2. **Domain Setup**: Configure custom domain (optional)
3. **Monitoring**: Set up CloudWatch dashboards
4. **Scaling**: Adjust Lambda memory/timeout as needed
5. **Security**: Review and tighten IAM permissions

---

**🚀 Your Enhanced CV Screening API will be live and secure on AWS!**

*Remember: Keep your credentials safe and never share them publicly.*