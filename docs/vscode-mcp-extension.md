# VS Code MCP Extension

A VS Code extension to connect the Parliament MCP server to GitHub Copilot Chat.

## Development Setup

1. Install VS Code Extension Development dependencies:
```bash
npm install -g @vscode/vsce yo generator-code
```

2. Generate extension scaffold:
```bash
yo code
```

3. Configure extension to communicate with MCP server at `http://localhost:8080/mcp/`

## Extension Features

- Connect to Parliament MCP server
- Expose parliamentary tools in VS Code command palette
- Integration with GitHub Copilot Chat (if API available)
- Quick access to constituency, member, and debate information

## Files Structure

```
parliament-mcp-vscode/
├── package.json          # Extension manifest
├── src/
│   ├── extension.ts      # Main extension code
│   ├── mcpClient.ts      # MCP protocol client
│   └── commands.ts       # VS Code commands
├── resources/            # Icons and assets
└── README.md
```

## Implementation Notes

The extension would need to:
1. Establish WebSocket/HTTP connection to MCP server
2. Implement MCP protocol for tool calling
3. Register VS Code commands for each parliamentary tool
4. Provide UI for displaying results

This is a custom development effort as VS Code doesn't currently have built-in MCP support.
