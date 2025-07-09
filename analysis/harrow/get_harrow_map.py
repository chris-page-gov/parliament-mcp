#!/usr/bin/env python3
"""
Get OS map showing roads between Harrow East and Harrow West
"""

import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async def get_harrow_map():
    """Get OS map tile for Harrow area showing constituency boundary roads"""
    print("🗺️  Getting OS Map for Harrow East/West Road Analysis")
    print("=" * 55)
    
    try:
        # Connect to OS NGD API server
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
                
                # List available tools
                tools = await session.list_tools()
                map_tools = [tool for tool in tools.tools if 'map' in tool.name.lower()]
                print(f"🗺️  Available map tools: {[tool.name for tool in map_tools]}")
                
                # Check if map tile tool is available
                if any(tool.name == "get_light_map_tile" for tool in tools.tools):
                    print("\n📍 Requesting OS map tile for Harrow area...")
                    
                    try:
                        # Request map tile for Harrow area
                        # Harrow is approximately at coordinates: 51.5836° N, -0.3339° W
                        # We'll request a tile that covers the area
                        
                        map_result = await session.call_tool("get_light_map_tile", {
                            "z": 14,  # Zoom level appropriate for road detail
                            "x": 8192,  # Approximate tile coordinates for Harrow
                            "y": 5462   # These would need to be calculated precisely
                        })
                        
                        print("🗺️  Map tile result:")
                        print(map_result.content)
                        
                        # The result should contain HTML with a downloadable map image
                        
                    except Exception as e:
                        print(f"⚠️  Map tile request failed: {e}")
                        print("Note: This tool may require a valid OS API key for map generation")
                
                else:
                    print("❌ Map tile tool not available")
                
                # Try alternative approach - get geographic data for the area
                print("\n📍 Getting geographic context for Harrow area...")
                
                try:
                    # Search for Harrow postcodes to get geographic context
                    harrow_postcodes = ["HA1 3TP", "HA2 7LX", "HA3 8LT"]  # Representative postcodes
                    
                    for postcode in harrow_postcodes:
                        try:
                            postcode_result = await session.call_tool("search_by_post_code", {
                                "postcode": postcode,
                                "format": "JSON",
                                "output_srs": "EPSG:4326"  # WGS84 for coordinates
                            })
                            print(f"\n📮 {postcode} location data:")
                            print(postcode_result.content)
                            
                        except Exception as e:
                            print(f"⚠️  Postcode {postcode} search failed: {e}")
                
                except Exception as e:
                    print(f"❌ Geographic data retrieval failed: {e}")
                
                # Provide manual map reference
                print("\n🗺️  Manual Map Reference:")
                print("For detailed OS mapping of Harrow East/West boundary roads:")
                print()
                print("📍 OS Map Coordinates:")
                print("• Grid Reference: TQ 15 88 (approximate center)")
                print("• Latitude/Longitude: 51.5836°N, -0.3339°W")
                print("• OS Landranger Map: Sheet 176 (West London)")
                print("• OS Explorer Map: Sheet 172 (Chiltern Hills East)")
                print()
                
                print("🛣️  Key Roads to Look For on OS Map:")
                key_roads = [
                    "A404 Harrow Road - Main east-west arterial",
                    "A4005 Northolt Road - Central Harrow connector", 
                    "A312 The Parkway - North-south route",
                    "B455 Pinner Road - Pinner to Harrow center",
                    "Harrow-on-the-Hill Station area - Boundary focal point"
                ]
                
                for road in key_roads:
                    print(f"• {road}")
                
                print()
                print("📱 Online OS Map Access:")
                print("• OS Maps website: https://osmaps.ordnancesurvey.co.uk/")
                print("• Search for 'Harrow, London' or postcode 'HA1 3TP'")
                print("• Zoom level 14-16 will show road detail and boundaries")
                print("• Use Layer options to show administrative boundaries")
                
                print("\n💡 Pro Tip:")
                print("The OS NGD API can provide detailed road network data")
                print("when a valid API key is configured. The map tile tool")
                print("would then generate actual downloadable OS map images.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(get_harrow_map())
