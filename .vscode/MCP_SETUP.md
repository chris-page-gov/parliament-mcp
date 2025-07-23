# 🔧 MCP Development Setup

## Quick Start

To set up VS Code MCP integration for development:

1. **Copy the template configuration:**
   ```bash
   cp .vscode/mcp.json.template .vscode/mcp.json
   ```

2. **Add your OS API key:**
   - Get an API key from [OS Data Hub](https://osdatahub.os.uk/)
   - Set the environment variable: `export OS_API_KEY="your_actual_key_here"`
   - Or edit `.vscode/mcp.json` directly (not recommended for security)

3. **Start VS Code:**
   - The MCP servers will automatically connect
   - Parliament MCP: Local development server
   - OS NGD API: Geographic data server

## Environment Variables

The MCP configuration expects:
- `OS_API_KEY` - Your Ordnance Survey API key
- `ENVIRONMENT` - Set to "local" for development

## MCP Servers Configured

### Parliament MCP
- **Purpose:** Access UK Parliament data (MPs, constituencies, votes, etc.)
- **Port:** Uses Python module execution
- **Location:** `/workspace/mcp_server`

### OS NGD API
- **Purpose:** UK geographic and mapping data
- **Port:** 8081 (HTTP transport)
- **Location:** `/workspace/os-mcp`

## Security Notes

⚠️ **Important:** Never commit your actual `mcp.json` file with real API keys!
- The actual `mcp.json` is gitignored
- Always use the template approach
- Keep your API keys in environment variables

## Troubleshooting

If MCP servers don't connect:
1. Check that both directories exist: `/workspace/mcp_server` and `/workspace/os-mcp`
2. Verify your OS API key is valid
3. Ensure ports aren't conflicting with other services
4. Check VS Code Developer Tools for MCP connection logs
