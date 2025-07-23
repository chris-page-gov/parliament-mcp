#!/usr/bin/env python3
"""
Enhanced Parliament MCP server with multiple API integration and historical data support.
This version integrates multiple official sources for comprehensive parliamentary data access.
"""

import asyncio
import aiohttp
import logging
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Type
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Create the MCP server
app = Server("Parliament MCP Server - Multi-API Enhanced")

# API Configuration
MEMBERS_API_BASE = "https://members-api.parliament.uk/api"
TWFY_API_BASE = "https://www.theyworkforyou.com/api"
DATA_PARLIAMENT_BASE = "https://data.parliament.uk"
HANSARD_WEB_BASE = "https://hansard.parliament.uk"

class ParliamentDataFederation:
    """Unified client for multiple Parliament APIs with intelligent fallback"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(3)  # Rate limiting
        self.cache: Dict[str, Any] = {}  # Simple in-memory cache for historical data
    
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={"User-Agent": "Parliament-MCP-Enhanced/1.0"}
        )
        return self
    
    async def __aexit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]):
        if self.session:
            await self.session.close()
    
    async def _api_call(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make API call with error handling"""
        if self.session is None:
            return {"error": "Session not initialized"}
            
        async with self.semaphore:
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"HTTP {response.status}", "url": url}
            except Exception as e:
                return {"error": str(e), "url": url}
    
    async def search_members_api(self, name: str, include_former: bool = True) -> Dict[str, Any]:
        """Search using the official Members API"""
        results: Dict[str, Any] = {}
        
        # Search current members
        url = f"{MEMBERS_API_BASE}/Members/Search"
        current_params: Dict[str, Any] = {"Name": name, "IsCurrentMember": True, "take": 20}
        results["current"] = await self._api_call(url, current_params)
        
        # Search former members if requested
        if include_former:
            former_params: Dict[str, Any] = {"Name": name, "IsCurrentMember": False, "take": 20}
            results["former"] = await self._api_call(url, former_params)
        
        return {
            "source": "UK Parliament Members API",
            "coverage": "Comprehensive for current, limited for historical",
            "results": results
        }
    
    async def search_theyworkforyou(self, name: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Search using TheyWorkForYou API for historical data"""
        cache_key = f"twfy_{name}_{date}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # TheyWorkForYou API calls
        results: Dict[str, Any] = {}
        
        # Search for person
        person_url = f"{TWFY_API_BASE}/getPerson"
        person_params: Dict[str, Any] = {"output": "js", "name": name}
        results["person_search"] = await self._api_call(person_url, person_params)
        
        # If we have a date, try to get constituency info for that period
        if date:
            # Get constituency for specific date (if API supports it)
            constituency_url = f"{TWFY_API_BASE}/getConstituency"
            constituency_params: Dict[str, Any] = {"output": "js", "name": name, "date": date}
            results["constituency_on_date"] = await self._api_call(constituency_url, constituency_params)
        
        result: Dict[str, Any] = {
            "source": "TheyWorkForYou API",
            "coverage": "Historical MPs from 1935 onwards",
            "date_queried": date,
            "results": results,
            "note": "TheyWorkForYou provides comprehensive historical MP data"
        }
        
        # Cache historical data (it doesn't change)
        if date and date < "2020-01-01":
            self.cache[cache_key] = result
        
        return result
    
    async def search_constituency_enhanced(self, search_text: Optional[str] = None, constituency_id: Optional[int] = None) -> Dict[str, Any]:
        """Enhanced constituency search with multiple sources"""
        results: Dict[str, Any] = {}
        
        # Try Members API first
        if search_text:
            url = f"{MEMBERS_API_BASE}/Location/Constituency/Search"
            params: Dict[str, Any] = {"searchText": search_text, "take": 20}
            results["members_api"] = await self._api_call(url, params)
        elif constituency_id:
            url = f"{MEMBERS_API_BASE}/Location/Constituency/{constituency_id}"
            results["members_api"] = await self._api_call(url)
        
        return {
            "source": "Enhanced Constituency Search",
            "search_text": search_text,
            "constituency_id": constituency_id,
            "results": results,
            "historical_note": "For historical constituency boundaries, additional research may be needed"
        }
    
    async def search_hansard_enhanced(self, query: str, date_from: str = None, date_to: str = None, 
                                    house: str = None, member_name: str = None) -> Dict[str, Any]:
        """Enhanced Hansard search with multiple approaches"""
        
        approaches = []
        results = {}
        
        # Approach 1: Try TheyWorkForYou for speeches/debates
        if query or member_name:
            approaches.append("theyworkforyou_debates")
            twfy_url = f"{TWFY_API_BASE}/getDebates"
            twfy_params = {"output": "js", "type": "commons"}
            if query:
                twfy_params["search"] = query
            if member_name:
                twfy_params["person"] = member_name
            if date_from:
                twfy_params["date"] = date_from
            
            results["theyworkforyou"] = await self._api_call(twfy_url, twfy_params)
        
        # Approach 2: Provide Hansard website guidance
        approaches.append("hansard_website_guidance")
        hansard_guidance = {
            "message": "For comprehensive Hansard search, use the official website",
            "url": f"{HANSARD_WEB_BASE}/search",
            "parameters": {
                "query": query,
                "date_from": date_from,
                "date_to": date_to,
                "house": house,
                "member": member_name
            },
            "note": "The Hansard website provides the most comprehensive search for parliamentary debates"
        }
        results["hansard_website"] = hansard_guidance
        
        # Approach 3: Historical context for old dates
        if date_from and date_from < "2000-01-01":
            approaches.append("historical_guidance")
            results["historical_guidance"] = {
                "message": f"For historical data from {date_from}, consider these sources:",
                "recommendations": [
                    "TheyWorkForYou.com covers debates from 1935 onwards",
                    "Parliament.uk historical archives",
                    "Physical Hansard volumes in libraries",
                    "Academic databases like HanSearch"
                ],
                "specific_apis": {
                    "theyworkforyou": "https://www.theyworkforyou.com/api/",
                    "parliament_data": "https://data.parliament.uk/"
                }
            }
        
        return {
            "query": query,
            "date_range": f"{date_from or 'earliest'} to {date_to or 'latest'}",
            "approaches_tried": approaches,
            "results": results,
            "summary": f"Found {len([r for r in results.values() if not isinstance(r, dict) or 'error' not in r])} data sources"
        }
    
    async def historical_member_lookup(self, name: str, target_date: str) -> Dict[str, Any]:
        """Comprehensive historical member lookup for specific dates"""
        
        all_results = {}
        data_sources = []
        
        # Source 1: Members API (for recent/current data)
        members_result = await self.search_members_api(name, include_former=True)
        all_results["members_api"] = members_result
        data_sources.append("UK Parliament Members API")
        
        # Source 2: TheyWorkForYou (for historical data)
        twfy_result = await self.search_theyworkforyou(name, target_date)
        all_results["theyworkforyou"] = twfy_result
        data_sources.append("TheyWorkForYou API")
        
        # Analysis
        analysis = self._analyze_historical_results(all_results, name, target_date)
        
        return {
            "search_name": name,
            "target_date": target_date,
            "data_sources": data_sources,
            "results": all_results,
            "analysis": analysis,
            "confidence": analysis.get("confidence", "unknown"),
            "recommendation": analysis.get("recommendation", "Manual verification recommended")
        }
    
    def _analyze_historical_results(self, results: Dict, name: str, date: str) -> Dict[str, Any]:
        """Analyze results from multiple sources to provide best answer"""
        
        analysis = {
            "confidence": "low",
            "findings": [],
            "recommendation": "Additional research needed"
        }
        
        # Check Members API results
        members_data = results.get("members_api", {}).get("results", {})
        if members_data.get("current") and not isinstance(members_data["current"], dict):
            analysis["findings"].append("Found in current Members API")
        
        if members_data.get("former") and not isinstance(members_data["former"], dict):
            analysis["findings"].append("Found in former Members API")
        
        # Check TheyWorkForYou results
        twfy_data = results.get("theyworkforyou", {}).get("results", {})
        if twfy_data.get("person_search") and not isinstance(twfy_data["person_search"], dict):
            analysis["findings"].append("Found in TheyWorkForYou database")
            analysis["confidence"] = "medium"
        
        # Date-specific analysis
        try:
            query_year = int(date[:4])
            if query_year < 1935:
                analysis["recommendation"] = f"For {query_year}, check physical parliamentary records"
            elif query_year < 2000:
                analysis["recommendation"] = "TheyWorkForYou API likely has this data"
                analysis["confidence"] = "medium"
            else:
                analysis["recommendation"] = "Check both Members API and TheyWorkForYou"
                analysis["confidence"] = "high"
        except:
            pass
        
        return analysis

# Global API client
federation = None

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools with enhanced historical capabilities"""
    return [
        Tool(
            name="search_constituency_multi_api",
            description="Enhanced constituency search using multiple official APIs with historical context",
            inputSchema={
                "type": "object",
                "properties": {
                    "searchText": {"type": "string", "description": "Search text for constituencies"},
                    "constituency_id": {"type": "integer", "description": "Specific constituency ID"},
                    "include_historical_context": {"type": "boolean", "description": "Include historical boundary information", "default": True}
                }
            }
        ),
        Tool(
            name="search_member_historical",
            description="Comprehensive historical member search - can answer questions like 'Was X an MP in 1992?'",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Member name to search for", "required": True},
                    "target_date": {"type": "string", "description": "Date to check if they were MP (YYYY-MM-DD format)"},
                    "include_current": {"type": "boolean", "description": "Include current members", "default": True},
                    "include_former": {"type": "boolean", "description": "Include former members", "default": True}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="search_hansard_multi_source",
            description="Enhanced Hansard search using multiple data sources for comprehensive historical coverage",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for debates/speeches"},
                    "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "house": {"type": "string", "enum": ["Commons", "Lords"], "description": "Parliamentary house"},
                    "member_name": {"type": "string", "description": "Specific member name"},
                    "include_historical_guidance": {"type": "boolean", "description": "Include guidance for historical searches", "default": True}
                }
            }
        ),
        Tool(
            name="get_api_federation_status",
            description="Check status and capabilities of all integrated Parliament APIs",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle enhanced tool calls with multiple API integration"""
    global federation
    
    try:
        async with ParliamentDataFederation() as fed:
            federation = fed
            
            if name == "search_constituency_multi_api":
                result = await handle_constituency_multi_api(arguments)
            elif name == "search_member_historical":
                result = await handle_member_historical(arguments)
            elif name == "search_hansard_multi_source":
                result = await handle_hansard_multi_source(arguments)
            elif name == "get_api_federation_status":
                result = await handle_federation_status()
            else:
                result = {"error": f"Unknown tool: {name}"}
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def handle_constituency_multi_api(args: dict) -> dict:
    """Handle enhanced constituency search"""
    search_text = args.get("searchText")
    constituency_id = args.get("constituency_id")
    include_historical = args.get("include_historical_context", True)
    
    result = await federation.search_constituency_enhanced(search_text, constituency_id)
    
    if include_historical:
        result["historical_context"] = {
            "note": "Constituency boundaries have changed over time",
            "recommendation": "For historical accuracy, verify boundary changes",
            "resources": [
                "https://www.boundarycommissionforengland.org.uk/",
                "https://en.wikipedia.org/wiki/Redistribution_of_Seats_Acts"
            ]
        }
    
    return result

async def handle_member_historical(args: dict) -> dict:
    """Handle comprehensive historical member search"""
    name = args.get("name")
    target_date = args.get("target_date")
    
    if not name:
        return {"error": "Member name is required"}
    
    if target_date:
        # Comprehensive historical lookup
        result = await federation.historical_member_lookup(name, target_date)
    else:
        # General member search
        result = await federation.search_members_api(name, args.get("include_former", True))
        twfy_result = await federation.search_theyworkforyou(name)
        result["additional_sources"] = {"theyworkforyou": twfy_result}
    
    return result

async def handle_hansard_multi_source(args: dict) -> dict:
    """Handle enhanced multi-source Hansard search"""
    return await federation.search_hansard_enhanced(
        args.get("query"),
        args.get("date_from"),
        args.get("date_to"),
        args.get("house"),
        args.get("member_name")
    )

async def handle_federation_status() -> dict:
    """Check status of all integrated APIs"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "federation_apis": {}
    }
    
    # Test Members API
    test_result = await federation._api_call(f"{MEMBERS_API_BASE}/Members/Search", {"Name": "Test", "take": 1})
    status["federation_apis"]["members_api"] = {
        "url": MEMBERS_API_BASE,
        "status": "available" if "error" not in test_result else "error",
        "capabilities": ["current_mps", "constituencies", "election_results"],
        "historical_coverage": "Limited - primarily recent years"
    }
    
    # Test TheyWorkForYou API
    twfy_test = await federation._api_call(f"{TWFY_API_BASE}/getPerson", {"output": "js", "name": "Test"})
    status["federation_apis"]["theyworkforyou"] = {
        "url": TWFY_API_BASE,
        "status": "available" if "error" not in twfy_test else "error",
        "capabilities": ["historical_mps", "debates", "voting_records"],
        "historical_coverage": "Excellent - from 1935 onwards"
    }
    
    # Hansard website guidance
    status["federation_apis"]["hansard_website"] = {
        "url": HANSARD_WEB_BASE,
        "status": "manual_access",
        "capabilities": ["comprehensive_debates", "historical_records"],
        "historical_coverage": "Complete - from 1803 onwards",
        "note": "Requires web interface or scraping"
    }
    
    status["federation_summary"] = {
        "total_apis": len(status["federation_apis"]),
        "historical_capability": "Enhanced - multiple sources for different time periods",
        "best_for_current": "Members API",
        "best_for_historical": "TheyWorkForYou API + Hansard website"
    }
    
    return status

async def main():
    """Main entry point for the enhanced multi-API stdio server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
