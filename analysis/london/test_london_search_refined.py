#!/usr/bin/env python3
"""
Test script for Parliament MCP server - Search London constituencies (refined)
This version filters out non-London constituencies more accurately.
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

async def test_london_constituencies_refined():
    """Test searching for all constituencies in the London area with better filtering"""
    try:
        # Import the MCP server components
        from mcp_server.app.api import search_constituency
        
        print("🏛️  Searching for all constituencies in the London area (refined)...")
        print("=" * 70)
        
        # London borough search terms
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
        
        # Keywords that indicate non-London constituencies
        exclude_keywords = [
            "Londonderry",  # Northern Ireland
            "Hull",         # Yorkshire
            "Northallerton", # North Yorkshire
            "Plymouth",     # Devon
            "Glastonbury",  # Somerset
            "Brentwood",    # Essex (though close to London, technically not Greater London)
            "Coldfield"     # Birmingham
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
                    
                    # Add unique constituencies, filtering out non-London ones
                    for constituency in constituencies:
                        if isinstance(constituency, dict):
                            constituency_id = constituency.get('id')
                            constituency_name = constituency.get('name', '')
                            
                            # Check if this constituency should be excluded
                            should_exclude = any(keyword in constituency_name for keyword in exclude_keywords)
                            
                            if constituency_id and constituency_id not in seen_ids and not should_exclude:
                                seen_ids.add(constituency_id)
                                all_constituencies.append(constituency)
                
            except Exception as e:
                print(f"Error searching for {term}: {e}")
                continue
        
        # Sort constituencies by name
        all_constituencies.sort(key=lambda x: x.get('name', ''))
        
        if all_constituencies:
            print(f"\n📍 Found {len(all_constituencies)} constituencies in Greater London:\n")
            
            # Group by London boroughs for better organization
            inner_london = []
            outer_london = []
            city_of_london = []
            
            for constituency in all_constituencies:
                name = constituency.get('name', 'Unknown')
                
                # Categorize constituencies
                if 'Cities of London and Westminster' in name:
                    city_of_london.append(constituency)
                elif any(area in name for area in ['Camden', 'Hackney', 'Hammersmith', 'Islington', 
                                                  'Kensington', 'Lambeth', 'Lewisham', 'Southwark', 
                                                  'Tower Hamlets', 'Wandsworth', 'Westminster']):
                    inner_london.append(constituency)
                else:
                    outer_london.append(constituency)
            
            # Display results by category
            if city_of_london:
                print("🏛️  **City of London:**")
                for constituency in city_of_london:
                    name = constituency.get('name', 'Unknown')
                    constituency_id = constituency.get('id', 'N/A')
                    current_rep = constituency.get('currentRepresentation', {})
                    member = current_rep.get('member', {}) if current_rep else {}
                    mp_name = member.get('nameDisplayAs', 'No current MP') if member else 'No current MP'
                    party = member.get('latestParty', {}) if member else {}
                    party_name = party.get('name', '') if party else ''
                    
                    print(f"• {name} (ID: {constituency_id})")
                    if mp_name != 'No current MP':
                        print(f"  └─ MP: {mp_name} ({party_name})")
                    print()
            
            if inner_london:
                print("🌆 **Inner London Boroughs:**")
                for constituency in inner_london:
                    name = constituency.get('name', 'Unknown')
                    constituency_id = constituency.get('id', 'N/A')
                    current_rep = constituency.get('currentRepresentation', {})
                    member = current_rep.get('member', {}) if current_rep else {}
                    mp_name = member.get('nameDisplayAs', 'No current MP') if member else 'No current MP'
                    party = member.get('latestParty', {}) if member else {}
                    party_name = party.get('name', '') if party else ''
                    
                    print(f"• {name} (ID: {constituency_id})")
                    if mp_name != 'No current MP':
                        print(f"  └─ MP: {mp_name} ({party_name})")
                    print()
            
            if outer_london:
                print("🏘️  **Outer London Boroughs:**")
                for constituency in outer_london:
                    name = constituency.get('name', 'Unknown')
                    constituency_id = constituency.get('id', 'N/A')
                    current_rep = constituency.get('currentRepresentation', {})
                    member = current_rep.get('member', {}) if current_rep else {}
                    mp_name = member.get('nameDisplayAs', 'No current MP') if member else 'No current MP'
                    party = member.get('latestParty', {}) if member else {}
                    party_name = party.get('name', '') if party else ''
                    
                    print(f"• {name} (ID: {constituency_id})")
                    if mp_name != 'No current MP':
                        print(f"  └─ MP: {mp_name} ({party_name})")
                    print()
            
            print(f"✅ Total Greater London constituencies found: {len(all_constituencies)}")
            print(f"   - City of London: {len(city_of_london)}")
            print(f"   - Inner London: {len(inner_london)}")
            print(f"   - Outer London: {len(outer_london)}")
            
        else:
            print("❌ No constituencies found")
            
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_london_constituencies_refined())
