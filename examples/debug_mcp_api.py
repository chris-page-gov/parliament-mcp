#!/usr/bin/env python3
"""
Simple test script to debug MCP API responses
"""

import asyncio
import aiohttp
import json


async def test_mcp_api():
    """Test the MCP API response format."""
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8080/mcp/",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        ) as response:
            print(f"Status: {response.status}")
            print(f"Headers: {dict(response.headers)}")
            
            content = await response.text()
            print(f"Raw content:\n{content}")
            print("-" * 50)
            
            # Try to parse as SSE
            if "event: message" in content and "data: " in content:
                lines = content.split('\n')
                for line in lines:
                    if line.startswith("data: "):
                        json_data = line[6:]  # Remove "data: " prefix
                        print(f"Found JSON data, length: {len(json_data)}")
                        try:
                            parsed = json.loads(json_data)
                            print(f"✅ Parsed successfully: {len(parsed.get('result', {}).get('tools', []))} tools found")
                            return parsed
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}")
                            print(f"First 100 chars: {json_data[:100]}")
            else:
                print("Not in SSE format, trying direct JSON parse...")
                try:
                    parsed = json.loads(content)
                    print(f"Direct parse successful: {parsed}")
                    return parsed
                except json.JSONDecodeError as e:
                    print(f"Direct JSON decode error: {e}")
            
            return None


if __name__ == "__main__":
    result = asyncio.run(test_mcp_api())
    if result and 'result' in result and 'tools' in result['result']:
        print(f"\n✅ Success! Found {len(result['result']['tools'])} tools:")
        for tool in result['result']['tools'][:3]:  # Show first 3
            print(f"  • {tool['name']}")
    else:
        print("\n❌ Failed to get tools")
