#!/usr/bin/env python3
"""
Test script for the Multi-API Enhanced Parliament MCP server
"""
import asyncio
import json
from parliament_mcp.mcp_server.multi_api_enhanced import ParliamentAPI

async def test_multi_api_server():
    """Test the multi-API server functionality"""
    print("🧪 Testing Parliament Multi-API Enhanced Server...")
    
    async with ParliamentAPI() as client:
        
        # Test 1: Search constituencies
        print("\n1️⃣ Testing constituency search...")
        constituency_result = await client.search_constituencies(search_text="London")
        print(f"   Constituency search status: {constituency_result.get('results', {}).get('search_results', {}).get('success', 'unknown')}")
        
        # Test 2: Historical member search (the Tim Eggar case)
        print("\n2️⃣ Testing historical member search...")
        historical_result = await client.search_historical_member("Tim Eggar", "1992-03-01")
        print(f"   Historical search completed: {len(historical_result.get('results', {}))} data sources checked")
        print(f"   Analysis findings: {len(historical_result.get('analysis', {}).get('findings', []))} findings")
        
        # Test 3: API status check
        print("\n3️⃣ Testing API status...")
        status_result = await client._safe_api_call(
            "https://members-api.parliament.uk/api/Members/Search", 
            {"Name": "Test", "take": 1}
        )
        print(f"   Members API status: {'✅ Available' if status_result.get('success') else '❌ Error'}")
        
        twfy_status = await client._safe_api_call(
            "https://www.theyworkforyou.com/api/getPerson",
            {"output": "js", "name": "Test"}
        )
        print(f"   TheyWorkForYou API status: {'✅ Available' if twfy_status.get('success') else '❌ Error'}")
        
        # Test 4: Enhanced Hansard search
        print("\n4️⃣ Testing enhanced Hansard search...")
        hansard_result = await client.search_hansard_multi_source(
            query="budget", 
            date_from="1992-03-01",
            member_name="Tim Eggar"
        )
        print(f"   Hansard search sources: {len(hansard_result.get('sources', {}))}")
        print(f"   Recommendations: {len(hansard_result.get('recommendations', []))}")

    print("\n✅ Multi-API server test completed!")
    print("\n🏛️ The enhanced server provides:")
    print("   • Historical MP data from 1935 onwards")
    print("   • Multiple API source integration")  
    print("   • Enhanced error handling")
    print("   • Comprehensive search guidance")

if __name__ == "__main__":
    asyncio.run(test_multi_api_server())
