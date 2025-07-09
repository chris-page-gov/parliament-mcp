# Parliament MCP Project - Updated Structure

**A comprehensive MCP (Model Context Protocol) implementation providing access to UK Parliament data and OS Geographic data through VS Code's native MCP support.**

> 📁 **This project has been reorganized for better maintainability and structure.**

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- VS Code with Dev Containers extension
- Docker (optional, for containerized deployment)

### Development Setup
1. **Open in VS Code**: Use the dev container for automatic setup
2. **MCP Servers**: Auto-configured in `.vscode/mcp.json`
3. **Run Analysis**: Use tools in `analysis/` directory
4. **View Maps**: Open files in `web/` directory

## 📁 New Project Structure

```
workspace/
├── 📋 Core MCP Servers
│   ├── mcp_server/          # Parliament MCP server implementation
│   ├── parliament_mcp/      # Parliament data processing
│   └── os-mcp/             # Real OS NGD API MCP server (external)
│
├── 🧪 Testing & Development  
│   ├── tests/mcp_tests/    # MCP server tests
│   ├── mock_servers/       # Mock implementations for development
│   └── logs/              # Test and runtime logs
│
├── 📊 Analysis & Tools
│   ├── analysis/london/    # London constituency analysis
│   ├── analysis/harrow/    # Harrow East/West road analysis
│   └── data/              # Generated data files
│
├── 🌐 Web Interface
│   └── web/               # HTML maps and visualizations
│
├── ⚙️ Infrastructure
│   ├── .devcontainer/     # VS Code dev container config
│   ├── .vscode/           # VS Code settings and MCP config
│   ├── terraform/         # Infrastructure as code
│   └── .github/           # GitHub workflows
```

## 🛠️ Available Tools

### London Constituency Analysis
```bash
# List all London constituencies
python analysis/london/london_constituencies_bulleted.py

# Search and filter London areas  
python analysis/london/test_london_search.py
```

### Harrow Road Analysis
```bash
# Analyze roads between Harrow East/West
python analysis/harrow/harrow_roads_analysis.py

# Generate OS maps for the area
python analysis/harrow/get_harrow_map.py

# View interactive map
open web/harrow_os_map.html
```

### MCP Server Testing
```bash
# Test real OS MCP server
python tests/mcp_tests/test_real_os_mcp.py

# Test OS NGD API integration
python tests/mcp_tests/test_os_ngd_api.py

# Basic connectivity tests
python tests/mcp_tests/simple_os_ngd_test.py
```

## 🔧 MCP Servers

### Parliament MCP Server (Port 8080)
- **Endpoint**: `http://localhost:8080`
- **Features**: MP data, constituency search, voting records
- **Configuration**: `mcp_server/` directory

### OS NGD API MCP Server (Port 8081)  
- **Endpoint**: `http://localhost:8081`
- **Features**: Geographic data, mapping, spatial analysis
- **Configuration**: `os-mcp/` directory

Both servers are automatically configured in VS Code via `.vscode/mcp.json`.

## 🗺️ Maps & Visualizations

### Interactive Maps
- **Harrow Constituency Map**: `web/harrow_os_map.html`
- **Secure Implementation**: No API key exposure
- **OS Map Integration**: Proper authentication patterns

### Data Outputs
- **London Constituencies**: `data/constituency_list.txt`
- **Analysis Results**: `logs/` directory

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

### VS Code Integration
MCP servers are configured in `.vscode/mcp.json` for native VS Code support.

## 🧪 Testing

All tests are organized in `tests/mcp_tests/`:
- Integration tests for both MCP servers
- Mock server implementations for development
- Connectivity and authentication verification

## 📚 Documentation

- **Project Structure**: `PROJECT_STRUCTURE.md`
- **Original README**: Preserved with original parliament MCP documentation
- **Contributing Guidelines**: `CONTRIBUTING.md`  
- **License**: `LICENSE`

## 🔧 Migration Notes

### What Changed
1. **Organized file structure** - Related files grouped in logical directories
2. **Updated import paths** - Tests and analysis tools use new structure
3. **Secure web files** - Removed API key exposure from HTML
4. **Centralized logs** - All logs moved to `logs/` directory
5. **Better separation** - Mock servers separated from real implementations

### Path Updates
- Test files: `tests/mcp_tests/`
- Analysis tools: `analysis/london/` and `analysis/harrow/`
- Web visualizations: `web/`
- Mock implementations: `mock_servers/`
- Data files: `data/`
- Logs: `logs/`

### Import Changes
```python
# Old
from os_ngd_mcp_server import OSNGDClient

# New  
from mock_servers.os_ngd_mcp_server import OSNGDClient
```

## 📄 License

MIT License - see `LICENSE` file for details.

---

For detailed MCP server documentation, see the original implementation documentation in the respective server directories.
