#!/usr/bin/env python3
"""
Simple script to start the Starlight Astrology API server
and display information about accessing the Swagger documentation.
"""

import uvicorn
import webbrowser
import time
import threading
from pathlib import Path

def open_browser():
    """Open browser to the Swagger documentation after a short delay."""
    time.sleep(3)  # Wait for server to start
    print("\n🌟 Opening Swagger Documentation in your browser...")
    webbrowser.open("http://localhost:8000/docs")

def main():
    print("🌟 Starlight Astrology API Server")
    print("=" * 50)
    print("🚀 Starting server on http://localhost:8000")
    print("📚 Swagger UI will be available at: http://localhost:8000/docs")
    print("📖 ReDoc documentation: http://localhost:8000/redoc")
    print("🔧 OpenAPI JSON schema: http://localhost:8000/openapi.json")
    print("=" * 50)
    
    # Open browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the server
    try:
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

if __name__ == "__main__":
    main() 