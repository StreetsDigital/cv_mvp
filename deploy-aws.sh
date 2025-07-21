#!/bin/bash

echo "🚀 Deploying Enhanced CV Screening to AWS Lambda..."

# Check if serverless is installed
if ! command -v serverless &> /dev/null; then
    echo "❌ Serverless Framework not found. Installing..."
    npm install -g serverless
fi

# Check if required plugins are installed
echo "📦 Installing Serverless plugins..."
npm init -y 2>/dev/null || true
npm install --save-dev serverless-python-requirements serverless-wsgi

# Check AWS credentials
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "⚠️  AWS credentials not found in environment."
    echo "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    echo "Or run: aws configure"
    exit 1
fi

# Check Anthropic API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not found in environment."
    echo "Please set your Anthropic API key:"
    echo "export ANTHROPIC_API_KEY='your-api-key-here'"
    exit 1
fi

# Copy optimized requirements
cp requirements-aws.txt requirements.txt

echo "🔧 Deploying to AWS Lambda..."
serverless deploy --verbose

echo "✅ Deployment complete!"
echo ""
echo "📍 Your API endpoints:"
serverless info --verbose

echo ""
echo "🧪 Test your deployment:"
echo "curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/health"