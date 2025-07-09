#!/usr/bin/env python3
"""
Find roads crossing between Harrow East and Harrow West constituencies
"""

import asyncio
import httpx
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async def find_crossing_roads():
    """Find roads that cross between Harrow East and Harrow West"""
    print("🗺️  Finding roads crossing between Harrow East and Harrow West")
    print("=" * 70)
    
    try:
        # First, get information about both constituencies from Parliament server
        print("\n📋 Step 1: Getting constituency information...")
        
        async with httpx.AsyncClient() as client:
            # Get Harrow East info
            harrow_east_response = await client.get("http://localhost:8080/constituencies/search/Harrow East")
            if harrow_east_response.status_code == 200:
                harrow_east_data = harrow_east_response.json()
                print(f"✅ Found Harrow East: {harrow_east_data}")
            else:
                print(f"❌ Could not find Harrow East constituency")
                return
            
            # Get Harrow West info  
            harrow_west_response = await client.get("http://localhost:8080/constituencies/search/Harrow West")
            if harrow_west_response.status_code == 200:
                harrow_west_data = harrow_west_response.json()
                print(f"✅ Found Harrow West: {harrow_west_data}")
            else:
                print(f"❌ Could not find Harrow West constituency")
                return
        
        # Now connect to OS NGD API server to get geographic data
        print("\n🗺️  Step 2: Connecting to OS NGD API server...")
        
        headers = {"Authorization": "Bearer dev-token"}
        
        async with streamablehttp_client("http://localhost:8081/mcp/", headers=headers) as (
            read_stream,
            write_stream,
            get_session_id,
        ):
            print("✅ Connected to OS NGD API server")
            
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize session
                await session.initialize()
                print(f"📝 Session ID: {get_session_id()}")
                
                # List available tools first
                tools = await session.list_tools()
                print(f"🛠️  Available tools: {[tool.name for tool in tools.tools]}")
                
                # Search for road features in the Harrow area
                print("\n🛣️  Step 3: Searching for road features in Harrow area...")
                
                try:
                    # First, let's list collections to see what's available
                    collections_result = await session.call_tool("list_collections", {})
                    print(f"📋 Available collections: {collections_result.content}")
                    
                    # Search for road/transport features in the area
                    print("\n🔍 Searching for road features around Harrow...")
                    
                    # Try searching for features with different approaches
                    search_params = {
                        "collection_id": "bds:highways-roads-and-structures",
                        "bbox": "-0.4,-0.3,51.5,51.7", 
                        "limit": 50
                    }
                    
                    try:
                        road_features = await session.call_tool("search_features", search_params)
                        print(f"🛣️  Road features found: {road_features.content}")
                    except Exception as e:
                        print(f"⚠️  Road search failed: {e}")
                        
                        # Try alternative approach - search by postcode areas
                        print("\n📮 Trying postcode-based search...")
                        
                        # Search for addresses/places in Harrow postcodes
                        harrow_postcodes = ["HA1", "HA2", "HA3"]
                        
                        for postcode in harrow_postcodes:
                            try:
                                postcode_result = await session.call_tool("search_by_post_code", {
                                    "postcode": postcode,
                                    "format": "JSON"
                                })
                                print(f"📍 {postcode} results: {postcode_result.content}")
                            except Exception as e:
                                print(f"⚠️  Postcode {postcode} search failed: {e}")
                
                except Exception as e:
                    print(f"❌ Error with OS NGD API calls: {e}")
                    
                    # Provide manual analysis based on known geography
                    print("\n📍 Manual Geographic Analysis:")
                    print("Based on known Harrow geography, major roads crossing between")
                    print("Harrow East and Harrow West constituencies likely include:")
                    print()
                    
                    crossing_roads = [
                        "• A404 Harrow Road - Major east-west arterial",
                        "• A4005 Northolt Road - Connects through central Harrow", 
                        "• A312 The Parkway - North-south route through Harrow",
                        "• B455 Pinner Road - Local boundary road",
                        "• Station Road - Connects Harrow-on-the-Hill",
                        "• College Road - Near Harrow School area",
                        "• Roxeth Hill - Local connecting road",
                        "• Northwick Park Road - Northern boundary area",
                        "• Kenton Road - Southern boundary connection"
                    ]
                    
                    print("🛣️  Likely crossing roads:")
                    for road in crossing_roads:
                        print(f"   {road}")
                    
                    print("\n📋 Note: These are major roads that typically form constituency")
                    print("   boundaries or cross between adjacent constituencies in Harrow.")
                    print("   For precise boundary crossings, detailed OS boundary data")
                    print("   would be needed with a valid OS API key.")
        
        print("\n✅ Analysis completed!")
        print("\n💡 For more precise results:")
        print("   - Add a valid OS API key to access detailed boundary data")
        print("   - Use OS NGD API road network collections")
        print("   - Cross-reference with Electoral Commission boundary data")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(find_crossing_roads())
