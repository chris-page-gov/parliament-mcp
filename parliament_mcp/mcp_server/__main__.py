"""
Entry point for running the Parliament MCP Multi-API Enhanced server.
"""

from parliament_mcp.mcp_server.multi_api_enhanced import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
