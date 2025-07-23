#!/usr/bin/env python3
"""
Stdio-only entry point for Parliament MCP server.
This creates a stdio-based MCP server for VS Code integration.
"""

import asyncio
import sys
from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp.types import EmptyResult, TextContent, Tool

from parliament_mcp.mcp_server.handlers import *
from parliament_mcp.settings import settings
from parliament_mcp.elasticsearch_helpers import get_async_es_client

class ParliamentMCPStdioServer:
    def __init__(self):
        self.server = Server("Parliament MCP Server")
        self.setup_tools()
    
    def setup_tools(self):
        """Setup MCP tools"""
        
        @self.server.call_tool()
        async def search_constituency(arguments):
            """Search for constituencies by name or get details by ID"""
            try:
                # Import handler function
                from parliament_mcp.mcp_server.handlers import search_constituency as search_handler
                
                # Initialize ES client
                async with get_async_es_client(settings) as es_client:
                    # Call the handler with ES client
                    result = await search_handler(
                        searchText=arguments.get("searchText"),
                        constituency_id=arguments.get("constituency_id"),
                        skip=arguments.get("skip", 0),
                        take=arguments.get("take", 5),
                        es_client=es_client
                    )
                    return [TextContent(type="text", text=str(result))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.list_tools()
        async def list_tools():
            """List available tools"""
            return [
                Tool(
                    name="search_constituency",
                    description="Search for UK Parliament constituencies by name or get details by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "searchText": {
                                "type": "string",
                                "description": "Search for constituencies by name or text"
                            },
                            "constituency_id": {
                                "type": "integer", 
                                "description": "Get comprehensive constituency details by ID"
                            },
                            "skip": {
                                "type": "integer",
                                "description": "Number of results to skip (for search)",
                                "default": 0
                            },
                            "take": {
                                "type": "integer",
                                "description": "Number of results to take (Max 20, for search). Default 5",
                                "default": 5
                            }
                        }
                    }
                )
            ]

    async def run(self):
        """Run the stdio server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """Main entry point"""
    server = ParliamentMCPStdioServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
