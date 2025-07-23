#!/usr/bin/env python3
"""
Simple Parliament MP Search - Testing Tim Eggar case
"""
import asyncio
import aiohttp
import json
from datetime import datetime

async def search_mp_historical(name: str, target_date: str = None):
    """Search for historical MP data"""
    
    async with aiohttp.ClientSession() as session:
        results = {
            "search_name": name,
            "target_date": target_date,
            "timestamp": datetime.now().isoformat(),
            "sources": {}
        }
        
        # UK Parliament Members API - Former Members
        print(f"🔍 Searching for {name} in UK Parliament API...")
        try:
            url = "https://members-api.parliament.uk/api/Members/Search"
            params = {"Name": name, "IsCurrentMember": "false", "take": 10}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results["sources"]["uk_parliament"] = {
                        "status": "success",
                        "total_results": data.get("totalResults", 0),
                        "members": []
                    }
                    
                    for item in data.get("items", []):
                        member = item.get("value", {})
                        membership = member.get("latestHouseMembership", {})
                        
                        member_info = {
                            "name": member.get("nameDisplayAs"),
                            "party": member.get("latestParty", {}).get("name"),
                            "constituency": membership.get("membershipFrom"),
                            "start_date": membership.get("membershipStartDate"),
                            "end_date": membership.get("membershipEndDate"),
                            "mp_id": member.get("id")
                        }
                        results["sources"]["uk_parliament"]["members"].append(member_info)
                        
                        print(f"   Found: {member_info['name']} ({member_info['constituency']}) {member_info['start_date']} to {member_info['end_date']}")
                        
                else:
                    results["sources"]["uk_parliament"] = {
                        "status": "error", 
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            results["sources"]["uk_parliament"] = {"status": "error", "error": str(e)}
        
        # Analysis for target date
        if target_date and results["sources"]["uk_parliament"].get("status") == "success":
            print(f"\n📅 Checking if {name} was MP on {target_date}...")
            
            target_dt = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
            
            for member in results["sources"]["uk_parliament"]["members"]:
                start_str = member["start_date"]
                end_str = member["end_date"]
                
                if start_str and end_str:
                    start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                    
                    if start_dt <= target_dt <= end_dt:
                        results["was_mp_on_date"] = True
                        results["constituency_on_date"] = member["constituency"]
                        results["party_on_date"] = member["party"]
                        print(f"✅ YES: {name} was MP for {member['constituency']} ({member['party']}) on {target_date}")
                        return results
            
            results["was_mp_on_date"] = False
            print(f"❌ NO: {name} was not an MP on {target_date}")
        
        return results

async def main():
    print("🏛️ Parliament MP Historical Search")
    print("=" * 50)
    
    # Test the Tim Eggar case
    result = await search_mp_historical("Tim Eggar", "1992-03-01")
    
    print(f"\n📊 FINAL RESULT:")
    print(f"   Name: {result['search_name']}")
    print(f"   Date: {result['target_date']}")
    print(f"   Was MP: {result.get('was_mp_on_date', 'Unknown')}")
    if result.get('constituency_on_date'):
        print(f"   Constituency: {result['constituency_on_date']}")
        print(f"   Party: {result['party_on_date']}")

if __name__ == "__main__":
    asyncio.run(main())
