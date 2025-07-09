#!/usr/bin/env python3
"""
Test script for Parliament MCP server - Search London constituencies
"""

import asyncio
import sys
import os
import json

# Add the workspace to the path
sys.path.insert(0, '/workspace')
sys.path.insert(0, '/workspace/mcp_server')

# Set environment
os.environ['ENVIRONMENT'] = 'local'

async def test_london_constituencies():
    """Test searching for all constituencies in the London area"""
    try:
        # Import the MCP server components
        from mcp_server.app.api import search_constituency
        
        print("🏛️  Searching for all constituencies in the London area...")
        print("=" * 60)
        
        # Try multiple search terms to find London area constituencies
        london_search_terms = [
            "London",
            "Westminster",
            "Camden",
            "Islington", 
            "Hackney",
            "Tower Hamlets",
            "Greenwich",
            "Lewisham",
            "Southwark",
            "Lambeth",
            "Wandsworth",
            "Hammersmith",
            "Kensington",
            "Chelsea",
            "Fulham",
            "Brent",
            "Ealing",
            "Hounslow",
            "Richmond",
            "Kingston",
            "Merton",
            "Sutton",
            "Croydon",
            "Bromley",
            "Bexley",
            "Barking",
            "Redbridge",
            "Waltham Forest",
            "Haringey",
            "Enfield",
            "Barnet",
            "Harrow",
            "Hillingdon"
        ]
        
        all_constituencies = []
        seen_ids = set()
        
        print("Searching for London boroughs and areas...")
        
        for term in london_search_terms:
            try:
                result = await search_constituency(searchText=term, take=50)
                
                if result:
                    # Parse the JSON response if it's a string
                    if isinstance(result, str):
                        try:
                            constituencies = json.loads(result)
                        except:
                            constituencies = []
                    elif isinstance(result, list):
                        constituencies = result
                    else:
                        constituencies = []
                    
                    # Add unique constituencies
                    for constituency in constituencies:
                        if isinstance(constituency, dict):
                            constituency_id = constituency.get('id')
                            if constituency_id and constituency_id not in seen_ids:
                                seen_ids.add(constituency_id)
                                all_constituencies.append(constituency)
                
            except Exception as e:
                print(f"Error searching for {term}: {e}")
                continue
        
        # Sort constituencies by name
        all_constituencies.sort(key=lambda x: x.get('name', ''))
        
        if all_constituencies:
            print(f"\n📍 Found {len(all_constituencies)} constituencies in the London area:\n")
            
            # Format as bulleted list
            for constituency in all_constituencies:
                name = constituency.get('name', 'Unknown')
                constituency_id = constituency.get('id', 'N/A')
                
                # Get current MP info if available
                current_rep = constituency.get('currentRepresentation', {})
                member = current_rep.get('member', {}) if current_rep else {}
                mp_name = member.get('nameDisplayAs', 'No current MP') if member else 'No current MP'
                party = member.get('latestParty', {}) if member else {}
                party_name = party.get('name', '') if party else ''
                
                print(f"• {name} (ID: {constituency_id})")
                if mp_name != 'No current MP':
                    print(f"  └─ MP: {mp_name} ({party_name})")
                print()
            
            print(f"✅ Total London area constituencies found: {len(all_constituencies)}")
        else:
            print("❌ No constituencies found")
            
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_london_constituencies())
