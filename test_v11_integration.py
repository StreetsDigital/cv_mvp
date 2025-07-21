#!/usr/bin/env python3
"""
Quick integration test for v1.1 enhancements
Tests basic functionality without full dependency installation
"""

import sys
import os
import importlib.util

def test_imports():
    """Test that all new modules can be imported"""
    print("Testing imports...")
    
    # Test WebSocket manager
    try:
        spec = importlib.util.spec_from_file_location(
            "websocket_manager", 
            "app/services/websocket_manager.py"
        )
        websocket_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(websocket_module)
        print("✅ WebSocket manager imports successfully")
    except Exception as e:
        print(f"❌ WebSocket manager import failed: {e}")
        return False
    
    # Test process explainer
    try:
        spec = importlib.util.spec_from_file_location(
            "process_explainer", 
            "app/explainers/process_explainer.py"
        )
        explainer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(explainer_module)
        print("✅ Process explainer imports successfully")
    except Exception as e:
        print(f"❌ Process explainer import failed: {e}")
        return False
    
    # Test enhanced processor v1.1
    try:
        spec = importlib.util.spec_from_file_location(
            "enhanced_cv_processor_v11", 
            "app/services/enhanced_cv_processor_v11.py"
        )
        processor_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(processor_module)
        print("✅ Enhanced processor v1.1 imports successfully")
    except Exception as e:
        print(f"❌ Enhanced processor v1.1 import failed: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        "app/services/websocket_manager.py",
        "app/endpoints/websocket_endpoints.py", 
        "app/explainers/process_explainer.py",
        "app/services/enhanced_cv_processor_v11.py",
        "frontend/js/realtime-cv-analyzer.js",
        "frontend/realtime-demo.html",
        "MODULAR_IMPLEMENTATION_PLAN.md",
        "V11_IMPLEMENTATION_SUMMARY.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False
    
    return all_exist

def test_main_py_integration():
    """Test that main.py has the new endpoints"""
    print("\nTesting main.py integration...")
    
    try:
        with open("app/main.py", "r") as f:
            content = f.read()
        
        checks = [
            ("WebSocket import", "from .endpoints.websocket_endpoints import"),
            ("Enhanced processor v1.1 import", "from .services.enhanced_cv_processor_v11 import"),
            ("WebSocket endpoint", "@app.websocket(\"/ws/analysis\")"),
            ("Real-time analysis endpoint", "/api/analyze-realtime")
        ]
        
        all_good = True
        for check_name, check_string in checks:
            if check_string in content:
                print(f"✅ {check_name}")
            else:
                print(f"❌ Missing: {check_name}")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error reading main.py: {e}")
        return False

def test_requirements():
    """Test that requirements.txt has WebSocket dependencies"""
    print("\nTesting requirements.txt...")
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        checks = [
            ("WebSocket dependency", "websockets=="),
            ("Redis dependency", "redis==")
        ]
        
        all_good = True
        for check_name, check_string in checks:
            if check_string in content:
                print(f"✅ {check_name}")
            else:
                print(f"❌ Missing: {check_name}")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("🚀 Running v1.1 Integration Tests\n")
    
    tests = [
        test_file_structure,
        test_imports,
        test_main_py_integration,
        test_requirements
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*50)
    if all(results):
        print("🎉 All tests passed! v1.1 integration is successful.")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)