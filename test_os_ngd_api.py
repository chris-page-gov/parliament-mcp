#!/usr/bin/env python3
"""
Test MCP server for OS NGD API functionality
This is a template/demo server - replace with actual API implementation
"""

import asyncio
import sys
import os
import json
from typing import Any, Dict, List

# Add the workspace to the path
sys.path.insert(0, '/workspace')
sys.path.insert(0, '/workspace/mcp_server')

# Set environment
os.environ['ENVIRONMENT'] = 'local'

class OSNGDAPIServer:
    """Mock OS NGD API server for testing"""
    
    def __init__(self):
        self.name = "OS NGD API Server"
        self.version = "1.0.0"
        
    async def get_geographic_data(self, location: str, data_type: str = "basic") -> Dict[str, Any]:
        """
        Mock function to get geographic data for a location
        In a real implementation, this would call the OS NGD API
        """
        # Mock response - replace with actual API calls
        mock_data = {
            "location": location,
            "data_type": data_type,
            "coordinates": {
                "latitude": 51.5074,
                "longitude": -0.1278
            },
            "administrative_areas": [
                {"name": "Greater London", "type": "region"},
                {"name": "City of Westminster", "type": "borough"}
            ],
            "postal_areas": [
                {"postcode": "SW1A 1AA", "area": "Westminster"}
            ],
            "boundaries": {
                "constituency": "Cities of London and Westminster",
                "ward": "St James's",
                "parish": None
            },
            "features": [
                {"name": "Buckingham Palace", "type": "landmark"},
                {"name": "Westminster Bridge", "type": "infrastructure"}
            ],
            "metadata": {
                "data_source": "OS NGD API (Mock)",
                "last_updated": "2025-01-09",
                "accuracy": "high"
            }
        }
        
        return mock_data
    
    async def search_places(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Mock function to search for places
        """
        # Mock search results
        mock_results = [
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
            for i in range(min(limit, 5))  # Limit mock results
        ]
        
        return mock_results
    
    async def get_boundaries(self, location: str, boundary_type: str = "all") -> Dict[str, Any]:
        """
        Mock function to get boundary information
        """
        mock_boundaries = {
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
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[
                    [-0.1278, 51.5074],
                    [-0.1270, 51.5074],
                    [-0.1270, 51.5080],
                    [-0.1278, 51.5080],
                    [-0.1278, 51.5074]
                ]]]
            }
        }
        
        return mock_boundaries

async def test_os_ngd_api():
    """Test the OS NGD API server functionality"""
    
    print("🗺️  Testing OS NGD API Server...")
    print("=" * 50)
    
    server = OSNGDAPIServer()
    
    try:
        # Test 1: Get geographic data for London
        print("\n📍 Test 1: Getting geographic data for London")
        london_data = await server.get_geographic_data("London", "detailed")
        print(json.dumps(london_data, indent=2))
        
        # Test 2: Search for places
        print("\n🔍 Test 2: Searching for places matching 'Westminster'")
        search_results = await server.search_places("Westminster", limit=3)
        print(json.dumps(search_results, indent=2))
        
        # Test 3: Get boundary information
        print("\n🗺️  Test 3: Getting boundary information for London")
        boundaries = await server.get_boundaries("London", "administrative")
        print(json.dumps(boundaries, indent=2))
        
        print("\n✅ OS NGD API Server tests completed successfully!")
        
        # Demonstrate integration with existing constituency data
        print("\n🏛️  Integration with Parliament data:")
        print("This server could be combined with the Parliament MCP server")
        print("to provide geographic context for constituencies.")
        
    except Exception as e:
        print(f"❌ Error testing OS NGD API server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_os_ngd_api())
