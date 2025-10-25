#!/usr/bin/env python3
"""
Agentic AI Course Pathway Recommender
Run script for the application
"""

import os
import sys
from app import app

def main():
    """Main function to run the application"""
    print("🚀 Starting Agentic AI Course Pathway Recommender...")
    print("=" * 60)
    
    # Check for required environment variables
    if not os.environ.get('GOOGLE_API_KEY'):
        print("⚠️  Warning: GOOGLE_API_KEY not found in environment variables")
        print("   The application will work with fallback recommendations")
        print("   To enable full AI features, set your Google API key")
        print()
    
    # Check if database exists
    if not os.path.exists('student_pathway.db'):
        print("📊 Initializing database...")
        from database import db_manager
        print("✅ Database initialized successfully")
    
    # Start the application
    print("🌐 Starting web server...")
    print("📍 Application will be available at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
        # Debug mode is controlled by the app.config['DEBUG'] setting
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
