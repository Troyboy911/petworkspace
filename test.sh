#!/bin/bash

# One-command local testing script
# Usage: ./test.sh

echo "🚀 Starting Pet Automation Suite locally..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys"
    echo "   Then run ./test.sh again"
    exit 0
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose -f docker-compose.local.yml up -d

# Wait for services
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

# Health check
echo "🏥 Checking application health..."
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo ""
    echo "✅ SUCCESS! Application is running!"
    echo ""
    echo "📊 Dashboard: http://localhost:5000"
    echo "🔍 Health: http://localhost:5000/health"
    echo ""
    echo "📝 View logs: docker-compose -f docker-compose.local.yml logs -f"
    echo "🛑 Stop: docker-compose -f docker-compose.local.yml down"
    echo ""
    
    # Try to open browser
    if command -v xdg-open > /dev/null; then
        xdg-open http://localhost:5000 2>/dev/null
    elif command -v open > /dev/null; then
        open http://localhost:5000 2>/dev/null
    fi
else
    echo "❌ Application failed to start. Checking logs..."
    docker-compose -f docker-compose.local.yml logs app
fi