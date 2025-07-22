"""
AWS Lambda handler for FastAPI application with enhanced CORS support
"""
import os
import json
from mangum import Mangum
from app.main import app
from app.middleware.cors_handler import CORSHandler

# Configure for Lambda environment
os.environ.setdefault("AWS_LAMBDA_FUNCTION_NAME", "cv-screening-api")

# Create Mangum handler
mangum_handler = Mangum(app, lifespan="off")

def handler(event, context):
    """
    Enhanced Lambda handler with CORS support
    Handles preflight requests and ensures CORS headers on all responses
    """
    try:
        # Handle OPTIONS preflight requests
        if event.get("httpMethod") == "OPTIONS":
            return CORSHandler.handle_preflight(event)
        
        # Process request with Mangum
        response = mangum_handler(event, context)
        
        # Ensure CORS headers are present
        response = CORSHandler.add_cors_headers(response)
        
        return response
        
    except Exception as e:
        # Return CORS-enabled error response
        print(f"Lambda handler error: {str(e)}")
        return CORSHandler.handle_error(e, status_code=500)