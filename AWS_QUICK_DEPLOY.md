# 🚀 AWS Lambda Quick Deploy Guide

## ✅ Your deployment is ready! Here's how to deploy:

### Step 1: Install Dependencies (One time only)
```bash
# Install Node.js from https://nodejs.org/ if not installed

# Install Serverless Framework
npm install -g serverless

# Install project dependencies
npm install
```

### Step 2: Set Environment Variables
```bash
# Set your AWS credentials
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### Step 3: Deploy to AWS
```bash
# Option 1: Use the deployment script
./deploy-aws.sh

# Option 2: Direct deployment
serverless deploy --verbose
```

### Step 4: Get Your API URL
After deployment completes, you'll see:
```
endpoints:
  ANY - https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/{proxy+}
  ANY - https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/
```

### Step 5: Test Your Deployment
```bash
# Health check
curl https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/health

# API config
curl https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/api/config

# CV Analysis
curl -X POST https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "John Smith, Software Engineer",
    "job_description": "Python Developer"
  }'
```

## 🎯 What Makes This Different from Vercel?

1. **No Python Version Issues**: AWS Lambda uses Python 3.9 (stable)
2. **No Heavy Dependencies**: Our requirements-aws.txt is optimized
3. **Better Control**: You manage the deployment environment
4. **More Memory/Timeout**: Up to 10GB RAM and 15 minutes timeout
5. **Cost Effective**: Pay only for what you use

## 📊 Expected Deployment Output

```
Deploying cv-screening-api to stage prod (us-east-1)

✔ Service deployed to stack cv-screening-api-prod (125s)

endpoints:
  ANY - https://abcd1234.execute-api.us-east-1.amazonaws.com/prod/{proxy+}
  ANY - https://abcd1234.execute-api.us-east-1.amazonaws.com/prod/
functions:
  api: cv-screening-api-prod-api (15 MB)
```

## 🛠 Useful Commands After Deployment

```bash
# View logs
serverless logs -f api -t

# Get deployment info
serverless info

# Remove deployment
serverless remove
```

## 💡 Pro Tips

1. **First deployment takes 2-3 minutes** - AWS is creating all resources
2. **Save your API URL** - You'll need it for your frontend
3. **Monitor costs** in AWS Cost Explorer (usually < $5/month)
4. **Set up CloudWatch alarms** for errors (optional)

## 🆘 Need Help?

Common issues:
- **"Serverless command not found"** → Run `npm install -g serverless`
- **"AWS credentials not configured"** → Check your environment variables
- **"Deployment failed"** → Check CloudFormation in AWS Console for details

Your deployment is optimized and ready to go! 🎉