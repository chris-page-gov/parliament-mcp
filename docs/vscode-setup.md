# Parliament MCP VS Code Configuration Summary

## ✅ Configuration Complete

Your VS Code is now fully configured for Parliament MCP development! Here's what has been set up:

### 📁 VS Code Configuration Files

- **`.vscode/settings.json`** - Python development settings, formatting, linting
- **`.vscode/tasks.json`** - Development tasks for building, testing, and running the MCP server
- **`.vscode/launch.json`** - Debug configurations using `debugpy`
- **`.vscode/extensions.json`** - Recommended extensions for MCP development
- **`.vscode/keybindings.json`** - Keyboard shortcuts for common tasks
- **`.vscode/setup.sh`** - Setup script for environment configuration

### 🚀 Quick Start

1. **Configure your environment** (if not done):
   ```bash
   ./.vscode/setup.sh
   ```

2. **Start debugging**: Press `F5` or use `Ctrl+Shift+P` → "Debug: Start Debugging"

3. **Run development tasks**: `Ctrl+Shift+P` → "Tasks: Run Task"

### ⌨️ Keyboard Shortcuts

- `Ctrl+Shift+M` - Start MCP Server
- `Ctrl+Shift+D` - Start Docker Services  
- `Ctrl+Shift+T` - Run Tests
- `Ctrl+Shift+E` - Check Elasticsearch Health
- `Ctrl+Shift+C` - Show Claude Config

### 🛠️ Available Tasks

| Task | Description |
|------|-------------|
| **Start MCP Server** | Run the MCP server locally with uv |
| **Start Docker Services** | Start Elasticsearch and other services |
| **Setup from Scratch** | Complete setup including data loading |
| **Run Tests** | Execute the test suite |
| **Initialize Elasticsearch** | Set up search indices |
| **Load Sample Data** | Load reference week data |
| **Show Claude Config** | Display Claude Desktop configuration |

### 🐛 Debug Configurations

- **Debug MCP Server** - Standard debugging
- **Debug MCP Server (with logs)** - Debug with detailed logging
- **Run Tests** - Debug test execution
- **Debug Specific Test** - Debug the currently open test file

### 🔧 Environment Details

- **Python Interpreter**: `.venv/bin/python` (managed by uv)
- **Virtual Environment**: Automatically created by uv
- **Dependencies**: Installed via `uv sync --group dev`
- **MCP Server**: Available at `http://localhost:8080/mcp/`

### 📦 Required Dependencies

✅ **Python 3.12** - Available  
✅ **uv** - Available  
✅ **parliament_mcp** - Installed  
✅ **boto3** - Added for AWS integration  
⚠️ **Node.js** - Required for mcp-remote (not in container)  
⚠️ **Docker** - Required for Elasticsearch (not in container)  

### 🎯 Next Steps

1. **Start the MCP server**:
   - Press `F5` for debugging
   - Or use task: "Start MCP Server"

2. **Connect to Claude Desktop**:
   - Run task: "Show Claude Config"
   - Copy the configuration to your Claude Desktop settings

3. **Load data** (requires Elasticsearch):
   - Run task: "Setup from Scratch"
   - Or manually: `make dev_setup_from_scratch`

### 🔍 Troubleshooting

- **Import errors**: Run `.vscode/setup.sh` to reinstall dependencies
- **Debugger issues**: Ensure `.venv/bin/python` exists and is executable
- **Task failures**: Check `.env` file configuration
- **MCP connection**: Verify server is running on port 8080

The configuration is optimized for the dev container environment where uv manages the virtual environment automatically, providing isolation while maintaining container efficiency.
