#!/bin/bash

# Parliament MCP VS Code Setup Script
# This script helps you configure your development environment

set -e

echo "🏛️  Parliament MCP VS Code Setup"
echo "================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating one from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "🔧 Please edit .env file and add your Azure OpenAI credentials:"
    echo "   - AZURE_OPENAI_API_KEY"
    echo "   - AZURE_OPENAI_ENDPOINT"
    echo "   - AZURE_OPENAI_RESOURCE_NAME"
    echo ""
    echo "📝 You can edit it now with: code .env"
    echo ""
    read -p "Press Enter to continue after you've configured .env..."
else
    echo "✅ .env file already exists"
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "⚠️  uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo "✅ uv installed"
else
    echo "✅ uv is available"
fi

# Install dependencies (uv will handle the environment automatically)
echo "📦 Installing Python dependencies..."
uv sync --group dev
echo "✅ Dependencies installed"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found. Please install Node.js to use mcp-remote"
    echo "   Visit: https://nodejs.org/"
else
    echo "✅ Node.js is available"
    
    # Install mcp-remote if not already installed
    if ! command -v mcp-remote &> /dev/null; then
        echo "📦 Installing mcp-remote..."
        npm install -g mcp-remote
        echo "✅ mcp-remote installed"
    else
        echo "✅ mcp-remote is available"
    fi
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Please install Docker to run Elasticsearch"
    echo "   Visit: https://docs.docker.com/get-docker/"
else
    echo "✅ Docker is available"
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
        echo "⚠️  Docker Compose not found. Please install Docker Compose"
    else
        echo "✅ Docker Compose is available"
    fi
fi

echo ""
echo "🎉 Setup complete! Here's what you can do next:"
echo ""
echo "1. 📝 Configure your .env file with Azure OpenAI credentials"
echo "2. 🐳 Start services: Ctrl+Shift+P → 'Tasks: Run Task' → 'Setup from Scratch'"
echo "3. 🔍 Or manually run: make dev_setup_from_scratch"
echo "4. 🐛 Debug the MCP server: F5 or Ctrl+Shift+P → 'Debug: Start Debugging'"
echo "5. 🧪 Run tests: Ctrl+Shift+P → 'Tasks: Run Task' → 'Run Tests'"
echo ""
echo "📋 Available VS Code tasks:"
echo "   - Start MCP Server"
echo "   - Start Docker Services"  
echo "   - Initialize Elasticsearch"
echo "   - Load Sample Data"
echo "   - Show Claude Config"
echo "   - Setup from Scratch"
echo ""
echo "🔗 MCP Server will be available at: http://localhost:8080/mcp/"
echo ""
echo "🧪 Testing configuration..."
if uv run python -c "import parliament_mcp; print('✅ Python imports working')" 2>/dev/null; then
    echo "✅ Python environment configured correctly"
    if uv run parliament-mcp --help >/dev/null 2>&1; then
        echo "✅ MCP CLI working correctly"
        echo "🚀 Your Parliament MCP development environment is ready!"
    else
        echo "⚠️  MCP CLI needs attention - check .env configuration"
    fi
else
    echo "⚠️  Python imports failed - check dependency installation"
fi
echo ""
