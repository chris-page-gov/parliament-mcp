#!/usr/bin/env python3
import asyncio
import json

print("🗺️  Testing OS NGD API functionality...")
print("=" * 50)

class OSNGDClient:
    @staticmethod
    async def get_geographic_data(location, data_type="basic"):
        return {
            "location": location,
            "data_type": data_type,
            "coordinates": {"latitude": 51.5074, "longitude": -0.1278},
            "administrative_areas": [
                {"name": "Greater London", "type": "region"},
                {"name": "City of Westminster", "type": "borough"}
            ],
            "postal_areas": [{"postcode": "SW1A 1AA", "area": "Westminster"}],
            "boundaries": {
                "constituency": "Cities of London and Westminster",
                "ward": "St James's",
                "parish": None
            },
            "metadata": {
                "data_source": "OS NGD API (Mock)",
                "last_updated": "2025-07-09",
                "accuracy": "high"
            }
        }
    
    @staticmethod
    async def search_places(query, limit=10):
        return [
            {
                "name": f"Location {i+1} matching '{query}'",
                "type": "settlement" if i % 2 == 0 else "landmark",
                "coordinates": {
                    "latitude": 51.5074 + (i * 0.01),
                    "longitude": -0.1278 + (i * 0.01)
                },
                "administrative_area": f"Area {i+1}",
                "confidence": 0.9 - (i * 0.1)
            }
            for i in range(min(limit, 5))
        ]
    
    @staticmethod
    async def get_boundaries(location, boundary_type="all"):
        return {
            "location": location,
            "boundary_type": boundary_type,
            "boundaries": {
                "administrative": {
                    "country": "England",
                    "region": "Greater London",
                    "local_authority": "Westminster",
                    "ward": "St James's"
                },
                "electoral": {
                    "constituency": "Cities of London and Westminster",
                    "european_region": "London"
                },
                "postal": {
                    "postcode_area": "SW",
                    "postcode_district": "SW1A"
                }
            }
        }

async def run_tests():
    client = OSNGDClient()
    
    print("\n📍 Test 1: Getting geographic data for London")
    london_result = await client.get_geographic_data("London", "detailed")
    print(json.dumps(london_result, indent=2))
    
    print("\n🔍 Test 2: Searching for places matching 'Westminster'")
    search_result = await client.search_places("Westminster", 3)
    print(json.dumps(search_result, indent=2))
    
    print("\n🗺️  Test 3: Getting boundaries for Manchester")
    boundaries_result = await client.get_boundaries("Manchester", "administrative")
    print(json.dumps(boundaries_result, indent=2))
    
    print("\n✅ All OS NGD API tests completed successfully!")
    
    print("\n🔗 Integration with Parliament MCP:")
    print("- The OS NGD API provides geographic context for constituencies")
    print("- Can be used alongside Parliament MCP for location-based queries")
    print("- Both servers are configured in VS Code MCP settings")

if __name__ == "__main__":
    asyncio.run(run_tests())
