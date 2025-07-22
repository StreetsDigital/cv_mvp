#!/usr/bin/env python3
"""
AWS Deployment Testing and Verification Script
Tests the application locally before AWS deployment
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_status(message, status="info"):
    """Print colored status messages"""
    if status == "success":
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
    elif status == "error":
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    elif status == "info":
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    print("\n🔐 Checking AWS Credentials...")
    
    # Check environment variables
    aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    
    if aws_key and aws_secret:
        print_status("AWS credentials found in environment", "success")
        print_status(f"AWS Region: {aws_region}", "info")
        return True
    
    # Check AWS CLI configuration
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            identity = json.loads(result.stdout)
            print_status(f"AWS CLI configured for account: {identity['Account']}", "success")
            return True
    except:
        pass
    
    print_status("AWS credentials not found", "error")
    print("\nTo configure AWS credentials:")
    print("1. Set environment variables:")
    print("   export AWS_ACCESS_KEY_ID='your-key'")
    print("   export AWS_SECRET_ACCESS_KEY='your-secret'")
    print("\n2. Or run: aws configure")
    return False

def check_anthropic_key():
    """Check if Anthropic API key is configured"""
    print("\n🔑 Checking Anthropic API Key...")
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key:
        print_status("Anthropic API key found", "success")
        return True
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            if 'ANTHROPIC_API_KEY' in f.read():
                print_status("Anthropic API key found in .env file", "warning")
                print("   Note: Set as environment variable for deployment")
                return True
    
    print_status("Anthropic API key not found", "error")
    print("\nSet your API key:")
    print("export ANTHROPIC_API_KEY='your-key-here'")
    return False

def check_serverless_framework():
    """Check if Serverless Framework is installed"""
    print("\n📦 Checking Serverless Framework...")
    
    try:
        result = subprocess.run(['serverless', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print_status(f"Serverless Framework installed: {version}", "success")
            return True
    except:
        pass
    
    print_status("Serverless Framework not installed", "error")
    print("\nInstall with:")
    print("npm install -g serverless")
    return False

def check_deployment_files():
    """Verify all required deployment files exist"""
    print("\n📄 Checking Deployment Files...")
    
    required_files = {
        'serverless.yml': 'Serverless configuration',
        'lambda_handler.py': 'Lambda entry point',
        'requirements-aws.txt': 'AWS-optimized dependencies',
        'deploy-aws.sh': 'Deployment script',
        'package.json': 'Node.js dependencies'
    }
    
    all_present = True
    for file, description in required_files.items():
        if Path(file).exists():
            print_status(f"{file} - {description}", "success")
        else:
            print_status(f"Missing {file} - {description}", "error")
            all_present = False
    
    return all_present

def test_local_import():
    """Test that the application can be imported"""
    print("\n🧪 Testing Local Import...")
    
    try:
        # Test lambda handler import
        from lambda_handler import handler
        print_status("Lambda handler imports successfully", "success")
        
        # Test FastAPI app import
        from app.main import app
        print_status("FastAPI application imports successfully", "success")
        
        # Test core services
        from app.services.cv_processor import CVProcessor
        from app.services.enhanced_cv_processor import EnhancedCVProcessor
        print_status("Core services import successfully", "success")
        
        return True
    except Exception as e:
        print_status(f"Import error: {str(e)}", "error")
        return False

def test_lambda_handler():
    """Test Lambda handler with a mock event"""
    print("\n🔧 Testing Lambda Handler...")
    
    try:
        from lambda_handler import handler
        
        # Mock API Gateway event
        test_event = {
            "httpMethod": "GET",
            "path": "/health",
            "headers": {"Content-Type": "application/json"},
            "body": None,
            "isBase64Encoded": False
        }
        
        # Mock context
        class MockContext:
            function_name = "test-function"
            memory_limit_in_mb = 128
            invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"
            aws_request_id = "test-request-id"
        
        response = handler(test_event, MockContext())
        
        if response.get('statusCode') == 200:
            print_status("Lambda handler test passed", "success")
            body = json.loads(response.get('body', '{}'))
            print_status(f"Health check response: {body}", "info")
            return True
        else:
            print_status(f"Lambda handler returned {response.get('statusCode')}", "error")
            return False
            
    except Exception as e:
        print_status(f"Lambda handler test failed: {str(e)}", "error")
        return False

def check_package_size():
    """Check deployment package size"""
    print("\n📦 Checking Package Size...")
    
    try:
        # Calculate approximate package size
        total_size = 0
        for root, dirs, files in os.walk('app'):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    total_size += os.path.getsize(filepath)
        
        # Add requirements estimate
        with open('requirements-aws.txt') as f:
            req_count = len([l for l in f if l.strip() and not l.startswith('#')])
        
        # Rough estimate: 2MB per dependency
        estimated_size = total_size + (req_count * 2 * 1024 * 1024)
        size_mb = estimated_size / (1024 * 1024)
        
        if size_mb < 50:
            print_status(f"Estimated package size: {size_mb:.1f}MB (Well under Lambda limit)", "success")
        elif size_mb < 250:
            print_status(f"Estimated package size: {size_mb:.1f}MB (Under Lambda limit)", "warning")
        else:
            print_status(f"Estimated package size: {size_mb:.1f}MB (May exceed Lambda limit)", "error")
            
        return size_mb < 250
        
    except Exception as e:
        print_status(f"Could not calculate package size: {str(e)}", "warning")
        return True

def generate_deployment_commands():
    """Generate deployment commands for the user"""
    print("\n🚀 Deployment Commands")
    print("=" * 60)
    
    print("\n1. First-time setup:")
    print("   npm install")
    print("   export ANTHROPIC_API_KEY='your-key-here'")
    print("   export AWS_ACCESS_KEY_ID='your-key'")
    print("   export AWS_SECRET_ACCESS_KEY='your-secret'")
    
    print("\n2. Deploy to AWS:")
    print("   ./deploy-aws.sh")
    print("   # or")
    print("   serverless deploy --verbose")
    
    print("\n3. After deployment:")
    print("   # View your endpoints")
    print("   serverless info")
    print("   ")
    print("   # Check logs")
    print("   serverless logs -f api -t")
    print("   ")
    print("   # Test health endpoint")
    print("   curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/health")

def run_deployment_tests():
    """Run all deployment tests"""
    print("🎯 AWS Deployment Readiness Test")
    print("=" * 60)
    
    tests = [
        ("Deployment Files", check_deployment_files),
        ("Local Import", test_local_import),
        ("Lambda Handler", test_lambda_handler),
        ("Package Size", check_package_size),
        ("AWS Credentials", check_aws_credentials),
        ("Anthropic API Key", check_anthropic_key),
        ("Serverless Framework", check_serverless_framework),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"{test_name} test failed: {str(e)}", "error")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT READINESS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Tests: {passed}/{total} passed")
    
    if passed == total:
        print_status("\n🎉 ALL TESTS PASSED - READY FOR AWS DEPLOYMENT!", "success")
        generate_deployment_commands()
        return True
    else:
        print_status(f"\n❌ {total - passed} tests failed - Please fix issues before deployment", "error")
        return False

if __name__ == "__main__":
    success = run_deployment_tests()
    sys.exit(0 if success else 1)