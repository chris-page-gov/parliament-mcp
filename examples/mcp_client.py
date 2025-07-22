#!/usr/bin/env python3
"""
Simple Python client to interact with the Parliament MCP server from VS Code.
"""

import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional


class ParliamentMCPClient:
    def __init__(self, base_url: str = "http://localhost:8080/mcp/"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool with the given arguments."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context.")
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        async with self.session.post(
            self.base_url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        ) as response:
            # Handle Server-Sent Events format
            content = await response.text()
            if content.startswith("event: message\ndata: "):
                json_data = content.split("data: ", 1)[1]
                return json.loads(json_data)
            else:
                return json.loads(content)

    async def list_tools(self) -> Dict[str, Any]:
        """List all available MCP tools."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context.")
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        async with self.session.post(
            self.base_url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        ) as response:
            # Handle Server-Sent Events format
            content = await response.text()
            if content.startswith("event: message\ndata: "):
                json_data = content.split("data: ", 1)[1]
                return json.loads(json_data)
            else:
                return json.loads(content)


async def main():
    """Example usage of the Parliament MCP client."""
    async with ParliamentMCPClient() as client:
        print("🏛️  Parliament MCP Client")
        print("=" * 40)
        
        # List available tools
        print("\n📋 Available Tools:")
        tools_response = await client.list_tools()
        if "result" in tools_response and "tools" in tools_response["result"]:
            for tool in tools_response["result"]["tools"]:
                print(f"  • {tool['name']}: {tool.get('description', 'No description')}")
        else:
            print("  Failed to retrieve tools")
            return
        
        print("\n" + "=" * 40)
        
        # Example: Search for a constituency
        print("\n🔍 Example: Searching for Birmingham constituencies...")
        constituency_response = await client.call_tool(
            "search_constituency",
            {"query": "Birmingham"}
        )
        
        if "result" in constituency_response:
            result = constituency_response["result"]
            if "content" in result:
                for content in result["content"]:
                    if content["type"] == "text":
                        print(content["text"])
        else:
            print("Search failed:", constituency_response.get("error", "Unknown error"))
        
        print("\n" + "=" * 40)
        
        # Example: Search for members
        print("\n👤 Example: Searching for members named 'Starmer'...")
        members_response = await client.call_tool(
            "search_members",
            {"name": "Starmer"}
        )
        
        if "result" in members_response:
            result = members_response["result"]
            if "content" in result:
                for content in result["content"]:
                    if content["type"] == "text":
                        print(content["text"])
        else:
            print("Search failed:", members_response.get("error", "Unknown error"))


if __name__ == "__main__":
    print("Starting Parliament MCP Client...")
    print("Make sure the MCP server is running on http://localhost:8080/mcp/")
    print()
    
    try:
        asyncio.run(main())
    except aiohttp.ClientConnectorError:
        print("❌ Error: Could not connect to MCP server.")
        print("   Make sure to start the server first:")
        print("   - Press F5 in VS Code to debug")
        print("   - Or run: uv run parliament-mcp serve")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
