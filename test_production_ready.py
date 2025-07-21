#!/usr/bin/env python3
"""
Production Readiness Test for Enhanced CV Screening v1.1
Validates core functionality before live deployment
"""

import sys
import os
import importlib.util
import json

def test_core_imports():
    """Test that all core modules can be imported without errors"""
    print("🧪 Testing Core Imports...")
    
    try:
        # Test main FastAPI app
        from app.main import app
        print("✅ FastAPI app imports successfully")
        
        # Test core services
        from app.services.chat_service import ChatService
        from app.services.cv_processor import CVProcessor
        from app.services.enhanced_cv_processor import EnhancedCVProcessor
        print("✅ Core services import successfully")
        
        # Test models
        from app.models.api_models import CVAnalysisRequest, CVAnalysisResponse
        from app.models.cv_models import CandidateCV, JobRequirements
        print("✅ Data models import successfully")
        
        # Test configuration
        from app.config import settings
        print("✅ Configuration loads successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_optional_imports():
    """Test optional imports that may not be available on serverless"""
    print("\n🔧 Testing Optional Imports...")
    
    # Test WebSocket availability
    try:
        from app.services.websocket_manager import websocket_manager
        print("✅ WebSocket manager available")
        websocket_available = True
    except ImportError:
        print("⚠️ WebSocket manager not available (expected on serverless)")
        websocket_available = False
    
    # Test v1.1 processor
    try:
        from app.services.enhanced_cv_processor_v11 import EnhancedCVProcessorV11
        print("✅ v1.1 processor available")
        v11_available = True
    except ImportError:
        print("⚠️ v1.1 processor not available (expected on serverless)")
        v11_available = False
    
    # Test optional dependencies
    try:
        from app.utils.optional_imports import get_feature_availability
        features = get_feature_availability()
        print(f"✅ Optional features: {features}")
    except ImportError:
        print("⚠️ Optional imports handler not available")
    
    return {
        'websocket': websocket_available,
        'v11': v11_available
    }

def test_api_models():
    """Test that API models can be instantiated"""
    print("\n📝 Testing API Models...")
    
    try:
        from app.models.api_models import CVAnalysisRequest, CVAnalysisResponse
        
        # Test request model
        request = CVAnalysisRequest(
            cv_text="John Smith, Software Engineer with 5 years experience",
            job_description="Senior Python Developer position"
        )
        print("✅ CVAnalysisRequest model works")
        
        # Test response model
        response = CVAnalysisResponse(
            overall_score=85.5,
            skills_match=80.0,
            experience_match=90.0,
            detailed_analysis={},
            recommendations=["Test recommendation"],
            candidate_name="John Smith",
            extracted_skills=["Python", "Software Engineering"]
        )
        print("✅ CVAnalysisResponse model works")
        
        return True
        
    except Exception as e:
        print(f"❌ Model error: {e}")
        return False

def test_configuration():
    """Test configuration settings"""
    print("\n⚙️ Testing Configuration...")
    
    try:
        from app.config import settings
        
        print(f"✅ App name: {settings.app_name}")
        print(f"✅ Debug mode: {settings.debug}")
        print(f"✅ Log level: {settings.log_level}")
        print(f"✅ Max file size: {settings.max_file_size_mb}MB")
        
        # Check if API key is configured (without exposing it)
        if hasattr(settings, 'anthropic_api_key') and settings.anthropic_api_key:
            print("✅ Anthropic API key configured")
        else:
            print("⚠️ Anthropic API key not configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        "app/main.py",
        "app/config.py",
        "app/services/chat_service.py",
        "app/services/cv_processor.py",
        "app/services/enhanced_cv_processor.py",
        "app/models/api_models.py",
        "app/models/cv_models.py",
        "requirements.txt",
        "vercel.json",
        "runtime.txt",
        "frontend/realtime-demo.html"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_deployment_config():
    """Test deployment configuration files"""
    print("\n🚀 Testing Deployment Configuration...")
    
    # Test vercel.json
    try:
        with open("vercel.json", "r") as f:
            vercel_config = json.load(f)
        
        if "builds" in vercel_config and "routes" in vercel_config:
            print("✅ vercel.json structure valid")
        else:
            print("❌ vercel.json missing required fields")
            return False
            
    except Exception as e:
        print(f"❌ vercel.json error: {e}")
        return False
    
    # Test runtime.txt
    try:
        with open("runtime.txt", "r") as f:
            runtime = f.read().strip()
        
        if "python" in runtime.lower():
            print(f"✅ runtime.txt: {runtime}")
        else:
            print(f"❌ Invalid runtime.txt: {runtime}")
            return False
            
    except Exception as e:
        print(f"❌ runtime.txt error: {e}")
        return False
    
    # Test requirements.txt
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()
        
        essential_packages = ["fastapi", "pydantic", "anthropic"]
        missing_packages = []
        
        for package in essential_packages:
            if package not in requirements.lower():
                missing_packages.append(package)
        
        if not missing_packages:
            print("✅ requirements.txt has essential packages")
        else:
            print(f"❌ Missing packages: {missing_packages}")
            return False
            
    except Exception as e:
        print(f"❌ requirements.txt error: {e}")
        return False
    
    return True

def run_production_tests():
    """Run all production readiness tests"""
    print("🚀 Enhanced CV Screening v1.1 - Production Readiness Test\n")
    
    tests = [
        ("Core Imports", test_core_imports),
        ("API Models", test_api_models),
        ("Configuration", test_configuration),
        ("File Structure", test_file_structure),
        ("Deployment Config", test_deployment_config)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Test optional features
    print("\n🔧 Optional Features Test...")
    optional_results = test_optional_imports()
    
    # Summary
    print("\n" + "="*60)
    print("📊 PRODUCTION READINESS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Core Tests: {passed}/{total} passed")
    
    if optional_results:
        print(f"🔧 Optional Features:")
        for feature, available in optional_results.items():
            status = "✅" if available else "⚠️"
            print(f"  {status} {feature.title()}: {'Available' if available else 'Not Available'}")
    
    print("\n" + "="*60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - READY FOR PRODUCTION DEPLOYMENT!")
        print("\n🚀 Next Steps:")
        print("1. Deploy to your chosen platform (Vercel, Railway, etc.)")
        print("2. Set environment variables (ANTHROPIC_API_KEY)")
        print("3. Test with sample data")
        print("4. Monitor performance and usage")
        return True
    else:
        print(f"❌ {total - passed} tests failed - Please fix issues before deployment")
        return False

if __name__ == "__main__":
    success = run_production_tests()
    sys.exit(0 if success else 1)