#!/usr/bin/env python3
"""
Simple server startup script for IDVerse
This script starts the Flask server with proper error handling
"""

import os
import sys
import subprocess
from pathlib import Path 

def main():
    """Start the IDVerse Flask server"""
    print("🚀 Starting IDVerse Server...")
    
    # Set environment variables
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'
    
    # Add project root to Python path
    project_root = Path(__file__).parent.absolute()
    sys.path.insert(0, str(project_root))
    
    try:
        # Import and create app
        from backend import create_app
        app = create_app()
        
        print("✅ App created successfully!")
        print("🌐 Starting server on http://127.0.0.1:5000")
        print("📝 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start the server
        app.run(debug=True, host='127.0.0.1', port=5000)
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("🔧 Try running: python -m pip install -r requirements.txt")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
