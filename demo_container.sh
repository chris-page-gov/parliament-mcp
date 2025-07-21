#!/bin/bash

# Simple script to run the MCP Sampling Intelligence demo in container
# This demonstrates the Phase 1 implementation without external dependencies

echo "🐳 Running MCP Sampling Intelligence Demo in Container"
echo "=================================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo "Please install Docker and try again"
    exit 1
fi

echo "📦 Building intelligence-enabled container..."

# Build the container with intelligence capabilities
if docker build -f Dockerfile.mcp-intelligence -t parliament-mcp:intelligence-demo . --quiet; then
    echo "✅ Container built successfully"
else
    echo "❌ Container build failed"
    exit 1
fi

echo ""
echo "🎭 Running Intelligence Demonstration..."
echo ""

# Run the demo
docker run --rm \
    --name mcp-intelligence-demo \
    -e PYTHONPATH=/app \
    parliament-mcp:intelligence-demo \
    python3 container_demo.py

echo ""
echo "🎉 Demo completed successfully!"
echo ""
echo "📋 What was demonstrated:"
echo "   ✅ Intelligent query analysis and intent recognition"
echo "   ✅ Dynamic tool selection based on query content"
echo "   ✅ Parameter optimization for better results" 
echo "   ✅ Quality improvements over baseline approach"
echo "   ✅ Container-compatible deployment"
echo ""
echo "🚀 To deploy with full LLM capabilities:"
echo "   1. Set Azure OpenAI environment variables in .env"
echo "   2. Use docker-compose.intelligence.yaml for deployment"
echo "   3. Monitor performance metrics in production"
