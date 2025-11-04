#!/usr/bin/env python3
"""
IDVerse Flask Application Entry Point
Run this file to start the Flask development server
"""

import sys
import os

# Add the project root to Python path so 'backend' module can be imported
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(os.path.join(project_root, '.env'))
except Exception:
    pass

from backend import create_app

if __name__ == "__main__":
    app = create_app()
    
    # Print all available routes for debugging
    print("\n" + "="*50)
    print("🚀 IDVerse Flask App Starting...")
    print("="*50)
    print("Available Routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule}")
    print("="*50)
    print("🌐 Server will be available at: http://localhost:5000")
    print("🔍 Health check: http://localhost:5000/health")
    print("📚 API docs: http://localhost:5000/_debug/routes")
    print("="*50 + "\n")
    
    # Start the Flask development server
    app.run(debug=True, host='127.0.0.1', port=5000)