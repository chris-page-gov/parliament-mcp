#!/usr/bin/env python3
"""
Test script for the real OS MCP server
"""

import asyncio
import logging
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_real_os_mcp():
    """Test the real OS MCP server"""
    # Set headers for dev testing authentication
    headers = {"Authorization": "Bearer dev-token"}

    logger.info("🔗 Connecting to OS MCP server at http://localhost:8081/mcp/")

    try:
        # Connect to server
        async with streamablehttp_client("http://localhost:8081/mcp/", headers=headers) as (
            read_stream,
            write_stream,
            get_session_id,
        ):
            logger.info("✅ Connection established")
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize
                logger.info("📋 Initializing session...")
                await session.initialize()
                print(f"✅ Initialized successfully")
                print(f"📝 Session ID: {get_session_id()}")

                # List tools
                logger.info("🔧 Listing available tools...")
                tools = await session.list_tools()
                print(f"🛠️  Available tools ({len(tools.tools)}):")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")

                # Test hello_world
                if any(tool.name == "hello_world" for tool in tools.tools):
                    try:
                        logger.info("🌍 Testing hello_world tool...")
                        result = await session.call_tool("hello_world", {"name": "VS Code User"})
                        print(f"📣 Hello World result: {result.content}")
                    except Exception as e:
                        print(f"❌ Error calling hello_world: {e}")

                # Test check_api_key
                if any(tool.name == "check_api_key" for tool in tools.tools):
                    try:
                        logger.info("🔐 Testing API key check...")
                        result = await session.call_tool("check_api_key", {})
                        print(f"🔑 API Key check result: {result.content}")
                    except Exception as e:
                        print(f"❌ Error checking API key: {e}")

                # Test list_collections
                if any(tool.name == "list_collections" for tool in tools.tools):
                    try:
                        logger.info("📊 Testing list_collections tool...")
                        result = await session.call_tool("list_collections", {})
                        print(f"📋 Collections result: {result.content}")
                    except Exception as e:
                        print(f"❌ Error calling list_collections: {e}")

                print("\n🎉 Real OS MCP server test completed!")
                print("🔗 This server provides comprehensive OS NGD API access")
                print("📍 Including geographic data, features, and spatial analysis")
                print("🗺️  Perfect complement to the Parliament MCP server")

    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        print("💡 Make sure the server is running on port 8081")
        print("🚀 Start with: python src/server.py --transport streamable-http --port 8081")


if __name__ == "__main__":
    asyncio.run(test_real_os_mcp())
