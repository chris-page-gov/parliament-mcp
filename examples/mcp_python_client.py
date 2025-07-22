#!/usr/bin/env python3
"""
Working Parliament MCP Client for VS Code
"""

import asyncio
import aiohttp
import json
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

    def _parse_sse_response(self, content: str) -> Dict[str, Any]:
        """Parse Server-Sent Events response format."""
        if "event: message" in content and "data: " in content:
            lines = content.split('\n')
            for line in lines:
                if line.startswith("data: "):
                    json_data = line[6:]  # Remove "data: " prefix
                    return json.loads(json_data)
        # Fallback to direct JSON parsing
        return json.loads(content)

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
            content = await response.text()
            return self._parse_sse_response(content)

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
            content = await response.text()
            return self._parse_sse_response(content)


async def main():
    """Example usage of the Parliament MCP client."""
    async with ParliamentMCPClient() as client:
        print("🏛️  Parliament MCP Client - Working Version")
        print("=" * 50)
        
        # List available tools
        print("\n📋 Available Tools:")
        try:
            tools_response = await client.list_tools()
            if "result" in tools_response and "tools" in tools_response["result"]:
                for i, tool in enumerate(tools_response["result"]["tools"], 1):
                    print(f"  {i:2d}. {tool['name']}")
                    # Show brief description (first line only)
                    desc = tool.get('description', 'No description').strip()
                    first_line = desc.split('\n')[0] if desc else 'No description'
                    print(f"      {first_line}")
                    print()
            else:
                print("  ❌ Failed to retrieve tools")
                return
        except Exception as e:
            print(f"  ❌ Error listing tools: {e}")
            return

        print(f"\n✅ Successfully connected to Parliament MCP server!")
        print(f"   {len(tools_response['result']['tools'])} tools available")
        
        # Test a simple tool call that doesn't require external APIs
        print(f"\n🔍 Testing server connectivity...")
        print("   (Note: Some tools may fail due to external API connectivity)")


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
