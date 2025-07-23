"""
Entry point for running the Parliament MCP server in stdio mode.
Usage: python -m parliament_mcp.mcp_server.stdio
"""

import asyncio
from mcp.server.stdio import stdio_server

from parliament_mcp.mcp_server.api import mcp_server

async def main():
    """Run the MCP server in stdio mode."""
    # Run the stdio server
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
