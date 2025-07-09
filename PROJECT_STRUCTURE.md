# Parliament MCP Project Structure

This project provides MCP (Model Context Protocol) servers for UK Parliament and OS Geographic data.

## 📁 Project Structure

```
workspace/
├── 📋 Core MCP Servers
│   ├── mcp_server/          # Parliament MCP server implementation
│   ├── parliament_mcp/      # Parliament data processing
│   └── os-mcp/             # Real OS NGD API MCP server (external)
│
├── 🧪 Testing & Development
│   ├── tests/
│   │   └── mcp_tests/      # MCP server tests
│   ├── mock_servers/       # Mock implementations for development
│   └── logs/              # Test and runtime logs
│
├── 📊 Analysis & Tools
│   ├── analysis/
│   │   ├── london/        # London constituency analysis
│   │   └── harrow/        # Harrow East/West road analysis
│   └── data/             # Generated data files
│
├── 🌐 Web Interface
│   └── web/              # HTML maps and visualizations
│
├── ⚙️ Infrastructure
│   ├── .devcontainer/    # VS Code dev container config
│   ├── .vscode/          # VS Code settings and MCP config
│   ├── terraform/        # Infrastructure as code
│   └── .github/          # GitHub workflows
│
└── 📚 Documentation
    ├── README.md
    ├── CONTRIBUTING.md
    └── LICENSE
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- VS Code with Dev Containers extension
- Docker (for containerized deployment)

### Development Setup
1. Open in VS Code dev container
2. MCP servers auto-configured in `.vscode/mcp.json`
3. Run tests: `python -m pytest tests/`

### Available MCP Servers
- **Parliament MCP** (port 8080): UK Parliament data
- **OS NGD API MCP** (port 8081): Geographic data and mapping

## 📊 Analysis Tools

### London Constituencies
- `analysis/london/london_constituencies_bulleted.py` - List all London constituencies
- `analysis/london/test_london_search.py` - Search and filter London areas

### Harrow Analysis
- `analysis/harrow/harrow_roads_analysis.py` - Roads between Harrow East/West
- `analysis/harrow/get_harrow_map.py` - Generate OS maps for the area
- `web/harrow_os_map.html` - Interactive map visualization

## 🧪 Testing

### MCP Server Tests
- `tests/mcp_tests/test_real_os_mcp.py` - Test real OS MCP server
- `tests/mcp_tests/test_os_ngd_api.py` - Test OS NGD API integration
- `tests/mcp_tests/simple_os_ngd_test.py` - Basic connectivity tests

### Mock Servers
- `mock_servers/os_ngd_mcp_server.py` - Mock OS NGD API for development

## 🌐 Web Interface

### Maps & Visualizations
- `web/harrow_os_map.html` - Interactive Harrow constituency map
- Secure implementation without API key exposure

## ⚙️ Configuration

### Environment Variables
```bash
# Parliament MCP Server
ENVIRONMENT=local

# OS NGD API MCP Server  
OS_API_KEY=your_os_api_key_here
STDIO_KEY=your_os_api_key_here
BEARER_TOKEN=dev-token
```

### VS Code MCP Integration
Configured in `.vscode/mcp.json` for native MCP support.

## 📚 Documentation

- **API Documentation**: See individual server README files
- **Contributing**: See `CONTRIBUTING.md`
- **License**: MIT (see `LICENSE`)

## 🔧 Maintenance

### Log Management
- All logs stored in `logs/` directory
- Structured by date and component
- Automatic cleanup recommended

### Data Updates
- Constituency data in `data/` directory
- Regenerate with analysis tools as needed
- Version control recommended for data files
