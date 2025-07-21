#!/bin/bash

# Build and run MCP Sampling Intelligence Demo in Container
# This script builds the updated container with intelligence capabilities and runs the demo

set -e

echo "🚀 Building MCP Sampling Intelligence Container..."

# Build the container with the updated dependencies
echo "📦 Building Docker image with OpenAI dependencies..."
docker build -f Dockerfile.mcp-server -t parliament-mcp:intelligence .

echo "🔧 Setting up container environment..."

# Create a temporary container to copy the demo script
echo "📋 Copying demo script to container..."
docker create --name temp-mcp parliament-mcp:intelligence
docker cp container_demo.py temp-mcp:/app/
docker commit temp-mcp parliament-mcp:intelligence-demo
docker rm temp-mcp

echo "🎭 Running Intelligence Demonstration..."

# Run the demonstration in the container
docker run --rm \
    --name mcp-intelligence-demo \
    -v "$(pwd)":/workspace \
    -e PYTHONPATH=/app \
    parliament-mcp:intelligence-demo \
    python3 /app/container_demo.py

echo ""
echo "✅ Container demo completed!"
echo ""
echo "🔧 To run the enhanced MCP server with intelligence in production:"
echo "   1. Set environment variables for Azure OpenAI:"
echo "      - AZURE_OPENAI_API_KEY"
echo "      - AZURE_OPENAI_ENDPOINT" 
echo "      - AZURE_OPENAI_API_VERSION"
echo ""
echo "   2. Update the container CMD to use enhanced_api.py:"
echo "      CMD [\"python3\", \"/app/parliament_mcp/mcp_server/enhanced_api.py\"]"
echo ""
echo "   3. Deploy using docker-compose with the intelligence-enabled image"
echo ""
echo "🎉 MCP Sampling Intelligence is ready for production deployment!"
