"""
AWS Lambda handler for FastAPI application
"""
import os
from mangum import Mangum
from app.main import app

# Configure for Lambda environment
os.environ.setdefault("AWS_LAMBDA_FUNCTION_NAME", "cv-screening-api")

# Create Lambda handler
handler = Mangum(app, lifespan="off")