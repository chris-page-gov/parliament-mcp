#!/usr/bin/env python3
"""
Test script for OS NGD API MCP server
"""

import asyncio
import sys
import os
import json

# Add the workspace to the path
sys.path.insert(0, '/workspace')

# Set environment
os.environ['ENVIRONMENT'] = 'local'

async def test_os_ngd_mcp_server():
    """Test the OS NGD API MCP server tools"""
    try:
        # Import the OS NGD client directly (simpler approach)
        from os_ngd_mcp_server import OSNGDClient
        
        print("🗺️  Testing OS NGD API MCP Server...")
        print("=" * 60)
        
        client = OSNGDClient()
        
        # Test 1: Get geographic data for London
        print("\n📍 Test 1: Getting geographic data for London")
        london_result = await client.get_geographic_data("London", "detailed")
        print(json.dumps(london_result, indent=2))
        
        # Test 2: Search for places
        print("\n🔍 Test 2: Searching for places matching 'Westminster'")
        search_result = await client.search_places("Westminster", 3)
        print(json.dumps(search_result, indent=2))
        
        # Test 3: Get boundary information
        print("\n🗺️  Test 3: Getting boundary information for Manchester")
        boundaries_result = await client.get_boundaries("Manchester", "administrative")
        print(json.dumps(boundaries_result, indent=2))
        
        # Test 4: Find constituency geography (integration test)
        print("\n🏛️  Test 4: Getting constituency geography for 'Cities of London and Westminster'")
        constituency_geo = await client.get_geographic_data("Cities of London and Westminster", "detailed")
        constituency_boundaries = await client.get_boundaries("Cities of London and Westminster", "electoral")
        
        constituency_result = {
            "constituency": "Cities of London and Westminster",
            "geographic_data": constituency_geo,
            "boundary_data": constituency_boundaries,
            "integration_note": "This data can be combined with Parliament MCP server for complete constituency information"
        }
        print(json.dumps(constituency_result, indent=2))
        
        print("\n✅ All OS NGD API MCP Server tests completed successfully!")
        
        print("\n🔗 Integration Notes:")
        print("- This OS NGD API server can work alongside the Parliament MCP server")
        print("- Geographic data can provide context for parliamentary constituencies")
        print("- Boundary information helps understand electoral geography")
        print("- Both servers are now configured in VS Code MCP settings")
        
    except Exception as e:
        print(f"❌ Error testing OS NGD API MCP server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_os_ngd_mcp_server())
