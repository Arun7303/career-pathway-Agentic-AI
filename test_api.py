#!/usr/bin/env python3
"""
Test script to check Google AI API connectivity and available models
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import google.generativeai as genai
from config import Config

def test_api_connection():
    """Test Google AI API connection and list available models"""
    
    print("🔍 Testing Google AI API Connection")
    print("=" * 50)
    
    # Check API key
    api_key = Config.GOOGLE_API_KEY
    print(f"API Key: {'*' * 20}{api_key[-4:] if api_key else 'NOT SET'}")
    
    if not api_key or api_key == 'your_actual_google_api_key_here':
        print("❌ API Key not properly configured")
        return False
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        print("✅ API configured successfully")
        
        # List available models
        print("\n📋 Available Models:")
        models = genai.list_models()
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
        
        # Test with a simple model
        print(f"\n🧪 Testing with model: {Config.MODEL_NAME}")
        model = genai.GenerativeModel(Config.MODEL_NAME)
        
        # Simple test
        response = model.generate_content("Hello, this is a test. Please respond with 'API working'.")
        if response and response.text:
            print(f"✅ API Test Successful: {response.text}")
            return True
        else:
            print("❌ API Test Failed: No response")
            return False
            
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Google AI API Test")
    print("=" * 60)
    
    success = test_api_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 API connection successful!")
        print("💡 The Google AI integration is working properly.")
    else:
        print("⚠️  API connection failed.")
        print("💡 Please check your API key and internet connection.")
        print("💡 You can get a free API key from: https://makersuite.google.com/app/apikey")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

