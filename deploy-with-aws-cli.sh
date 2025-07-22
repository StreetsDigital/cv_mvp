#!/bin/bash

echo "🚀 Deploying Enhanced CV Screening API using AWS CLI & SAM..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    case $2 in
        "success") echo -e "${GREEN}✅ $1${NC}" ;;
        "warning") echo -e "${YELLOW}⚠️  $1${NC}" ;;
        "error") echo -e "${RED}❌ $1${NC}" ;;
        "info") echo -e "${BLUE}ℹ️  $1${NC}" ;;
        *) echo "$1" ;;
    esac
}

# Check prerequisites
print_status "Checking prerequisites..." "info"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    print_status "AWS CLI not found. Please install it first." "error"
    echo "Installation: https://aws.amazon.com/cli/"
    exit 1
fi

# Check SAM CLI
if ! command -v sam &> /dev/null; then
    print_status "AWS SAM CLI not found. Installing..." "warning"
    
    # Try to install SAM CLI
    if command -v brew &> /dev/null; then
        brew tap aws/tap
        brew install aws-sam-cli
    else
        print_status "Please install AWS SAM CLI manually:" "error"
        echo "https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
        exit 1
    fi
fi

# Check AWS credentials
print_status "Checking AWS credentials..." "info"
if ! aws sts get-caller-identity &> /dev/null; then
    print_status "AWS credentials not configured." "error"
    echo "Run: aws configure"
    exit 1
fi

# Get AWS account info
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region || echo "us-east-1")
print_status "AWS Account: $AWS_ACCOUNT, Region: $AWS_REGION" "success"

# Check Anthropic API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    print_status "ANTHROPIC_API_KEY not set." "error"
    echo "Run: export ANTHROPIC_API_KEY='your-key-here'"
    exit 1
fi

# Prepare deployment
print_status "Preparing deployment files..." "info"

# Copy optimized requirements for Lambda
cp requirements-aws.txt requirements.txt

# Create S3 bucket for deployment artifacts (if it doesn't exist)
BUCKET_NAME="cv-screening-deployments-$AWS_ACCOUNT-$AWS_REGION"
print_status "Creating S3 bucket for deployment artifacts..." "info"

if ! aws s3 ls "s3://$BUCKET_NAME" 2>/dev/null; then
    if [ "$AWS_REGION" = "us-east-1" ]; then
        aws s3 mb "s3://$BUCKET_NAME"
    else
        aws s3 mb "s3://$BUCKET_NAME" --region "$AWS_REGION"
    fi
    print_status "Created S3 bucket: $BUCKET_NAME" "success"
else
    print_status "Using existing S3 bucket: $BUCKET_NAME" "info"
fi

# Build the application
print_status "Building application with SAM..." "info"
sam build --use-container

if [ $? -ne 0 ]; then
    print_status "Build failed!" "error"
    exit 1
fi

print_status "Build completed successfully!" "success"

# Deploy the application
print_status "Deploying to AWS..." "info"

sam deploy \
    --template-file .aws-sam/build/template.yaml \
    --stack-name cv-screening-api \
    --s3-bucket "$BUCKET_NAME" \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides AnthropicApiKey="$ANTHROPIC_API_KEY" \
    --region "$AWS_REGION" \
    --no-confirm-changeset

if [ $? -ne 0 ]; then
    print_status "Deployment failed!" "error"
    exit 1
fi

# Get outputs
print_status "Getting deployment information..." "info"
API_URL=$(aws cloudformation describe-stacks \
    --stack-name cv-screening-api \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
    --output text \
    --region "$AWS_REGION")

LAMBDA_ARN=$(aws cloudformation describe-stacks \
    --stack-name cv-screening-api \
    --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionArn`].OutputValue' \
    --output text \
    --region "$AWS_REGION")

print_status "🎉 Deployment completed successfully!" "success"
echo ""
echo "📍 Your API is live at:"
echo "   $API_URL"
echo ""
echo "🔧 Lambda Function ARN:"
echo "   $LAMBDA_ARN"
echo ""
echo "🧪 Test your deployment:"
echo "   curl $API_URL/health"
echo ""
echo "📊 Monitor your function:"
echo "   aws logs tail /aws/lambda/cv-screening-api --follow"
echo ""
echo "🗑️  To remove the deployment:"
echo "   aws cloudformation delete-stack --stack-name cv-screening-api --region $AWS_REGION"
echo ""

# Test the deployment
print_status "Testing deployment..." "info"
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    print_status "Health check passed!" "success"
    echo "Response: $HEALTH_RESPONSE"
else
    print_status "Health check failed. Check logs:" "warning"
    echo "aws logs tail /aws/lambda/cv-screening-api --follow"
fi

print_status "🚀 Enhanced CV Screening API is now live on AWS!" "success"