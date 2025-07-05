#!/bin/bash
# Simple script to start the Starlight Astrology API server

echo "🌟 Starting Starlight Astrology API Server..."
echo "📚 Swagger Documentation will be available at: http://localhost:8000/docs"
echo "📖 ReDoc Documentation will be available at: http://localhost:8000/redoc"
echo "🔧 OpenAPI JSON Schema will be available at: http://localhost:8000/openapi.json"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload 