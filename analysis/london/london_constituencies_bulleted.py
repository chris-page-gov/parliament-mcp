#!/usr/bin/env python3
"""
Get London constituencies in bulleted list format
"""

# Comprehensive list of Greater London parliamentary constituencies (2024 boundaries)
london_constituencies = [
    "Barking",
    "Battersea", 
    "Beckenham and Penge",
    "Bermondsey and Old Southwark",
    "Bethnal Green and Stepney",
    "Bexleyheath and Crayford",
    "Brent East",
    "Brent West", 
    "Brentford and Isleworth",
    "Bromley and Biggin Hill",
    "Camberwell and Peckham",
    "Carshalton and Wallington",
    "Chelsea and Fulham",
    "Chingford and Woodford Green",
    "Chislehurst and Sidcup",
    "Cities of London and Westminster",
    "Croydon East",
    "Croydon South", 
    "Croydon West",
    "Dagenham and Rainham",
    "Dulwich and West Norwood",
    "Ealing Central and Acton",
    "Ealing North",
    "Ealing Southall",
    "East Ham",
    "Edmonton and Winchmore Hill",
    "Eltham and Chislehurst",
    "Enfield North",
    "Erith and Thamesmead",
    "Feltham and Heston",
    "Finchley and Golders Green",
    "Greenwich and Woolwich",
    "Hackney North and Stoke Newington",
    "Hackney South and Shoreditch",
    "Hammersmith and Chiswick",
    "Hampstead and Highgate",
    "Harrow East",
    "Harrow West",
    "Hayes and Harlington",
    "Hendon",
    "Holborn and St Pancras",
    "Hornchurch and Upminster",
    "Hornsey and Friern Barnet",
    "Ilford North",
    "Ilford South",
    "Islington North",
    "Islington South and Finsbury",
    "Kensington and Bayswater",
    "Kingston and Surbiton",
    "Lewisham East",
    "Lewisham North",
    "Lewisham West and East Dulwich",
    "Leyton and Wanstead",
    "Mitcham and Morden",
    "New Malden",
    "Newham East",
    "Newham West",
    "Old Bexley and Sidcup",
    "Orpington",
    "Putney",
    "Queen's Park and Maida Vale",
    "Richmond Park",
    "Romford",
    "Ruislip, Northwood and Pinner",
    "Southgate and Wood Green",
    "Streatham and Croydon North",
    "Sutton and Cheam",
    "Tooting",
    "Tottenham",
    "Twickenham",
    "Uxbridge and South Ruislip",
    "Vauxhall and Camberwell Green",
    "Walthamstow",
    "Wandsworth",
    "West Ham and Beckton",
    "Westminster North",
    "Wimbledon"
]

def print_london_constituencies():
    """Print London constituencies as a bulleted list"""
    print("🏛️  Greater London Parliamentary Constituencies")
    print("=" * 50)
    print()
    
    # Sort alphabetically and print as bulleted list
    for constituency in sorted(london_constituencies):
        print(f"• {constituency}")
    
    print()
    print(f"✅ Total: {len(london_constituencies)} constituencies in Greater London")
    print()
    print("📋 Note: This list reflects the 2024 constituency boundaries")
    print("   and includes all parliamentary seats within the Greater London Authority area.")

if __name__ == "__main__":
    print_london_constituencies()
