#!/bin/bash
# Google Cloud Run deployment script

echo "🚀 Deploying CV Screener to Google Cloud Run"

# Set variables
PROJECT_ID="your-project-id"
SERVICE_NAME="cv-screener-automateengage"
REGION="us-central1"

# Authenticate (run this manually first: gcloud auth login)
# gcloud config set project $PROJECT_ID

# Build and push container
echo "📦 Building container..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --concurrency 100 \
  --timeout 300 \
  --set-env-vars="APP_NAME=CV Automation MVP,DEBUG=false,LOG_LEVEL=INFO"

echo "✅ Deployment complete!"
echo "🌐 Your app will be available at: https://$SERVICE_NAME-$REGION.run.app"
echo "🔧 Don't forget to set your ANTHROPIC_API_KEY:"
echo "   gcloud run services update $SERVICE_NAME --region $REGION --set-env-vars ANTHROPIC_API_KEY=your_key_here"