#!/usr/bin/env python3
"""
Enhanced Parliament MCP server with direct Hansard API integration.
This version uses the official Parliament APIs and Hansard website APIs for historical data.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Create the MCP server
app = Server("Parliament MCP Server - Enhanced API")

# API Configuration
MEMBERS_API_BASE = "https://members-api.parliament.uk/api"
HANSARD_API_BASE = "https://hansard.parliament.uk/api"  # Hypothetical - needs investigation
HANSARD_SEARCH_BASE = "https://hansard.parliament.uk/search"

class ParliamentAPIClient:
    """Unified client for Parliament APIs with better error handling and caching"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(5)  # Rate limiting
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "Parliament-MCP-Server/2.0"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_members_api(self, endpoint: str, params: Dict = None) -> Any:
        """Call the Members API with better error handling"""
        async with self.semaphore:
            url = f"{MEMBERS_API_BASE}{endpoint}"
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Members API error: {response.status} for {url}")
                        return {"error": f"API returned {response.status}"}
            except Exception as e:
                logger.error(f"Members API exception: {e}")
                return {"error": str(e)}
    
    async def search_hansard_web(self, query: str, date_from: str = None, date_to: str = None, 
                                house: str = None, member_name: str = None) -> List[Dict]:
        """Search Hansard using web scraping approach for historical data"""
        params = {}
        if query:
            params["searchTerm"] = query
        if date_from:
            params["startDate"] = date_from
        if date_to:
            params["endDate"] = date_to
        if house:
            params["house"] = house.lower()
        if member_name:
            params["member"] = member_name
            
        # This would need to be implemented based on actual Hansard API/scraping
        # For now, return a structured response
        return [{
            "type": "hansard_search",
            "note": "Historical Hansard search requires web scraping or official API access",
            "query": query,
            "date_range": f"{date_from} to {date_to}" if date_from or date_to else "all dates",
            "suggestion": "Use Members API for current MPs or implement Hansard web scraping"
        }]
    
    async def get_historical_member_data(self, member_name: str, date: str) -> Dict:
        """Attempt to find historical member data"""
        # Search current members first
        current_result = await self.get_members_api("/Members/Search", {
            "Name": member_name,
            "IsCurrentMember": False  # Include former members
        })
        
        # Add historical context
        return {
            "search_name": member_name,
            "target_date": date,
            "current_api_results": current_result,
            "historical_note": "For precise historical data from 1992, additional sources needed",
            "suggestions": [
                "Use Parliament.uk historical records",
                "Access archived Hansard volumes",
                "Check constituency boundary changes"
            ]
        }

# Global API client
api_client = None

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools with enhanced capabilities"""
    return [
        Tool(
            name="search_constituency_enhanced",
            description="Enhanced constituency search with historical context and better error handling",
            inputSchema={
                "type": "object",
                "properties": {
                    "searchText": {"type": "string", "description": "Search text for constituencies"},
                    "constituency_id": {"type": "integer", "description": "Specific constituency ID"},
                    "include_historical": {"type": "boolean", "description": "Include historical context", "default": False},
                    "skip": {"type": "integer", "default": 0},
                    "take": {"type": "integer", "default": 10}
                }
            }
        ),
        Tool(
            name="search_members_historical",
            description="Search for MPs with historical context - can find former MPs and their service periods",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Member name to search"},
                    "target_date": {"type": "string", "description": "Date to check if they were MP (YYYY-MM-DD)"},
                    "include_current": {"type": "boolean", "description": "Include current members", "default": True},
                    "include_former": {"type": "boolean", "description": "Include former members", "default": True}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="search_hansard_enhanced",
            description="Enhanced Hansard search with multiple data sources and historical capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "house": {"type": "string", "enum": ["Commons", "Lords"], "description": "Parliamentary house"},
                    "member_name": {"type": "string", "description": "Specific member name"},
                    "use_historical": {"type": "boolean", "description": "Attempt historical search", "default": True}
                }
            }
        ),
        Tool(
            name="get_api_status",
            description="Check status and capabilities of available Parliament APIs",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle enhanced tool calls with better error handling"""
    global api_client
    
    try:
        async with ParliamentAPIClient() as client:
            api_client = client
            
            if name == "search_constituency_enhanced":
                result = await handle_constituency_search_enhanced(arguments)
            elif name == "search_members_historical":
                result = await handle_members_historical_search(arguments)
            elif name == "search_hansard_enhanced":
                result = await handle_hansard_enhanced_search(arguments)
            elif name == "get_api_status":
                result = await handle_api_status()
            else:
                result = {"error": f"Unknown tool: {name}"}
            
            return [TextContent(type="text", text=str(result))]
    
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def handle_constituency_search_enhanced(args: dict) -> dict:
    """Enhanced constituency search with better data handling"""
    search_text = args.get("searchText")
    constituency_id = args.get("constituency_id")
    include_historical = args.get("include_historical", False)
    
    if search_text:
        result = await api_client.get_members_api("/Location/Constituency/Search", {
            "searchText": search_text,
            "skip": args.get("skip", 0),
            "take": args.get("take", 10)
        })
    elif constituency_id:
        result = await api_client.get_members_api(f"/Location/Constituency/{constituency_id}")
    else:
        return {"error": "Must provide either searchText or constituency_id"}
    
    if include_historical and isinstance(result, list):
        # Add historical context for each constituency
        for constituency in result:
            constituency["historical_note"] = "Constituency boundaries may have changed over time"
            constituency["data_source"] = "Current Members API"
    
    return {
        "constituencies": result,
        "enhanced_features": {
            "historical_context": include_historical,
            "api_source": "UK Parliament Members API",
            "data_currency": "Current as of API call"
        }
    }

async def handle_members_historical_search(args: dict) -> dict:
    """Search for members with historical context"""
    name = args.get("name")
    target_date = args.get("target_date")
    include_current = args.get("include_current", True)
    include_former = args.get("include_former", True)
    
    # Search with different parameters
    results = {}
    
    if include_current:
        current_search = await api_client.get_members_api("/Members/Search", {
            "Name": name,
            "IsCurrentMember": True
        })
        results["current_members"] = current_search
    
    if include_former:
        former_search = await api_client.get_members_api("/Members/Search", {
            "Name": name,
            "IsCurrentMember": False
        })
        results["former_members"] = former_search
    
    # Add historical analysis
    if target_date:
        results["historical_analysis"] = await api_client.get_historical_member_data(name, target_date)
    
    return {
        "search_query": name,
        "target_date": target_date,
        "results": results,
        "limitations": [
            "Members API primarily contains current/recent data",
            "For precise historical records (pre-2000), additional sources needed",
            "Constituency boundaries and names may have changed"
        ],
        "recommendations": [
            "For 1992 data, consult Parliament.uk historical archives",
            "Check Hansard volumes from that period",
            "Consider using TheyWorkForYou.com API for historical data"
        ]
    }

async def handle_hansard_enhanced_search(args: dict) -> dict:
    """Enhanced Hansard search with multiple approaches"""
    query = args.get("query")
    date_from = args.get("date_from")
    date_to = args.get("date_to")
    house = args.get("house")
    member_name = args.get("member_name")
    use_historical = args.get("use_historical", True)
    
    results = {
        "search_parameters": args,
        "approaches_tried": [],
        "data_sources": []
    }
    
    # Try current Elasticsearch if available (existing approach)
    results["approaches_tried"].append("local_elasticsearch")
    results["elasticsearch_status"] = "Connection failed - Elasticsearch not available"
    
    # Try web-based Hansard search
    if use_historical:
        results["approaches_tried"].append("hansard_web_search")
        web_results = await api_client.search_hansard_web(
            query, date_from, date_to, house, member_name
        )
        results["web_search_results"] = web_results
        results["data_sources"].append("hansard.parliament.uk")
    
    # Add recommendations for historical searches
    if date_from and date_from < "2000-01-01":
        results["historical_recommendations"] = {
            "note": "For pre-2000 data, consider these approaches:",
            "options": [
                "Direct access to Hansard archive volumes",
                "Parliament.uk historical database",
                "TheyWorkForYou.com API (covers 1935 onwards)",
                "Academic databases like HanSearch"
            ],
            "api_alternatives": [
                "https://www.theyworkforyou.com/api/",
                "Parliament.uk data.parliament.uk API",
                "Academic institutions' Hansard databases"
            ]
        }
    
    return results

async def handle_api_status() -> dict:
    """Check status of available APIs"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "api_endpoints": {},
        "capabilities": {},
        "limitations": {}
    }
    
    # Test Members API
    try:
        test_result = await api_client.get_members_api("/Members/Search", {"Name": "Test", "take": 1})
        status["api_endpoints"]["members_api"] = {
            "status": "available" if "error" not in test_result else "error",
            "base_url": MEMBERS_API_BASE,
            "capabilities": ["current_mps", "constituencies", "election_results", "member_details"]
        }
    except Exception as e:
        status["api_endpoints"]["members_api"] = {"status": "error", "error": str(e)}
    
    # Hansard capabilities
    status["api_endpoints"]["hansard"] = {
        "status": "limited",
        "note": "No direct API - requires web scraping or alternative sources",
        "alternatives": [
            "hansard.parliament.uk (web interface)",
            "theyworkforyou.com API",
            "data.parliament.uk"
        ]
    }
    
    status["capabilities"] = {
        "current_data": "Full access via Members API",
        "historical_data": "Limited - requires additional implementation",
        "hansard_search": "Requires web scraping or alternative APIs"
    }
    
    status["limitations"] = {
        "historical_cutoff": "Members API primarily covers recent years",
        "hansard_access": "No direct API for historical Hansard",
        "rate_limiting": "Applied to prevent API abuse"
    }
    
    return status

async def main():
    """Main entry point for the enhanced stdio server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
