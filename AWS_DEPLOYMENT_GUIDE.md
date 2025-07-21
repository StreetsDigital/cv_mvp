# 🚀 AWS Lambda Deployment Guide for Enhanced CV Screening

## 📋 Prerequisites

### 1. AWS Account Setup
- AWS account with programmatic access
- AWS CLI installed and configured
- IAM user with Lambda, API Gateway, and CloudFormation permissions

### 2. Required Tools
```bash
# Install Node.js (for Serverless Framework)
# Download from: https://nodejs.org/

# Install Serverless Framework globally
npm install -g serverless

# Install AWS CLI (if not already installed)
# macOS: brew install awscli
# Windows: Download from AWS website
```

### 3. Environment Variables
```bash
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## 🚀 Quick Deployment

### Option 1: One-Command Deploy
```bash
./deploy-aws.sh
```

### Option 2: Step-by-Step
```bash
# 1. Install dependencies
npm install

# 2. Deploy to AWS
serverless deploy

# 3. Check deployment info
serverless info
```

## 🔧 Configuration Options

### Environment Stages
```bash
# Deploy to development
serverless deploy --stage dev

# Deploy to production
serverless deploy --stage prod

# Deploy to custom stage
serverless deploy --stage staging
```

### Custom Region
```bash
serverless deploy --region us-west-2
```

### Custom Memory/Timeout
Edit `serverless.yml`:
```yaml
provider:
  memorySize: 2048  # Increase for better performance
  timeout: 60       # Max 15 minutes for Lambda
```

## 📊 Expected Deployment Output

```
✅ Service deployed successfully!

Service Information
service: cv-screening-api
stage: prod
region: us-east-1
stack: cv-screening-api-prod
resources: 12
api keys:
  None
endpoints:
  ANY - https://abcd1234ef.execute-api.us-east-1.amazonaws.com/prod/{proxy+}
  ANY - https://abcd1234ef.execute-api.us-east-1.amazonaws.com/prod/
functions:
  api: cv-screening-api-prod-api (15 MB)
```

## 🧪 Testing Your Deployment

### Health Check
```bash
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/health
```

### API Configuration
```bash
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/api/config
```

### CV Analysis Test
```bash
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "John Smith, Software Engineer with 5 years Python experience",
    "job_description": "Looking for Senior Python Developer with FastAPI experience"
  }'
```

## 📈 Performance & Costs

### Lambda Performance
- **Cold Start**: ~2-3 seconds (first request)
- **Warm Requests**: ~200-500ms
- **Memory**: 1024MB (configurable)
- **Timeout**: 30 seconds (configurable up to 15 minutes)

### Estimated Costs (Monthly)
- **API Gateway**: ~$3.50/million requests
- **Lambda**: ~$0.20/million requests (1GB memory)
- **CloudWatch Logs**: ~$0.50/GB stored
- **Total for 100K requests/month**: ~$1-2

## 🛠 Management Commands

### View Logs
```bash
# Real-time logs
serverless logs -f api -t

# Recent logs
serverless logs -f api
```

### Update Deployment
```bash
# Redeploy with changes
serverless deploy

# Deploy single function
serverless deploy -f api
```

### Remove Deployment
```bash
serverless remove
```

## 🔒 Security Features

### Built-in Security
- ✅ HTTPS by default (API Gateway)
- ✅ IAM-based access control
- ✅ VPC support (if needed)
- ✅ AWS WAF integration available
- ✅ CloudWatch monitoring included

### Environment Variables
All sensitive data stored as encrypted environment variables:
- `ANTHROPIC_API_KEY`
- Custom configuration options

### CORS Configuration
Automatically configured for web app integration.

## 📊 Monitoring & Debugging

### CloudWatch Integration
- Automatic logging to CloudWatch
- Performance metrics included
- Error tracking and alerts

### Debug Mode
Add to `serverless.yml`:
```yaml
provider:
  environment:
    DEBUG: true
    LOG_LEVEL: DEBUG
```

## 🚨 Troubleshooting

### Common Issues

**1. Deployment Timeout**
```bash
# Increase timeout in serverless.yml
provider:
  deploymentBucket:
    maxPreviousDeploymentArtifacts: 5
```

**2. Package Too Large**
```bash
# Check package size
serverless package
# Optimize by excluding unnecessary files
```

**3. Import Errors**
```bash
# Check Lambda logs
serverless logs -f api
```

**4. Permission Errors**
```bash
# Ensure AWS credentials have required permissions:
# - Lambda:*
# - APIGateway:*
# - CloudFormation:*
# - S3:* (for deployment artifacts)
```

## 🎯 Production Optimizations

### Performance Tuning
```yaml
# In serverless.yml
provider:
  memorySize: 1536    # Increase for faster processing
  timeout: 60         # Allow longer processing time
  reservedConcurrency: 10  # Limit concurrent executions
```

### Custom Domain (Optional)
```yaml
plugins:
  - serverless-domain-manager

custom:
  customDomain:
    domainName: api.yourcompany.com
    certificateName: '*.yourcompany.com'
    createRoute53Record: true
```

## 🔗 Integration Options

### Frontend Integration
Update your frontend to use the AWS API Gateway URL:
```javascript
const API_BASE_URL = 'https://your-api-id.execute-api.us-east-1.amazonaws.com/prod';
```

### Custom Headers
AWS API Gateway automatically handles:
- CORS headers
- Request/response transformations
- Rate limiting (if configured)

## 🎉 Ready for Production!

Your Enhanced CV Screening API is now:
- ✅ **Deployed on AWS Lambda** with auto-scaling
- ✅ **Secured with HTTPS** via API Gateway
- ✅ **Cost-optimized** with pay-per-request pricing
- ✅ **Monitored** with CloudWatch integration
- ✅ **Production-ready** with proper error handling

### Next Steps:
1. **Test thoroughly** with sample data
2. **Configure custom domain** (optional)
3. **Set up monitoring alerts** in CloudWatch
4. **Document API endpoints** for your team
5. **Scale as needed** by adjusting memory/timeout settings

---

**🚀 Your Enhanced CV Screening v1.1 is now live on AWS! 🎯**

*Deployed with Claude Code - Enterprise-grade serverless architecture*