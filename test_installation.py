#!/usr/bin/env python3
"""
Test script to verify the installation and basic functionality
"""

import sys
import importlib
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        'flask',
        'pandas',
        'numpy',
        'sklearn',
        'google.generativeai',
        'sqlite3',
        'json',
        'logging'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

def test_database():
    """Test database functionality"""
    print("\n🗄️  Testing database functionality...")
    
    try:
        from database import db_manager
        print("✅ Database module imported successfully")
        
        # Test database initialization
        db_manager.init_database()
        print("✅ Database initialization successful")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_agents():
    """Test AI agents functionality"""
    print("\n🤖 Testing AI agents...")
    
    try:
        from agents.agentic_orchestrator import agentic_orchestrator
        print("✅ Agentic orchestrator imported successfully")
        
        # Test agent status
        status = agentic_orchestrator.get_agent_status()
        print(f"✅ Agent status check successful: {status['active_agents']}/{status['total_agents']} agents active")
        
        return True
    except Exception as e:
        print(f"❌ Agents test failed: {e}")
        return False

def test_flask_app():
    """Test Flask application"""
    print("\n🌐 Testing Flask application...")
    
    try:
        from app import app
        print("✅ Flask app imported successfully")
        
        # Test app configuration
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Home page accessible")
            else:
                print(f"⚠️  Home page returned status code: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_google_api():
    """Test Google API configuration"""
    print("\n🔑 Testing Google API configuration...")
    
    try:
        from config import Config
        api_key = Config.GOOGLE_API_KEY
        
        if api_key and api_key != 'your_actual_google_api_key_here':
            print("✅ Google API key configured")
            return True
        else:
            print("⚠️  Google API key not configured (fallback mode will be used)")
            return True  # This is not a failure, just a warning
    except Exception as e:
        print(f"❌ Google API test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Agentic AI Course Pathway Recommender - Installation Test")
    print("=" * 70)
    
    tests = [
        ("Package Imports", test_imports),
        ("Database", test_database),
        ("AI Agents", test_agents),
        ("Flask Application", test_flask_app),
        ("Google API", test_google_api)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("🚀 Run 'python run.py' to start the application")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
