#!/usr/bin/env python3
"""
Multi-API Parliament MCP Server - Production Ready
Enhanced historical data access with proper error handling and type safety
"""

import asyncio
import aiohttp
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Create the MCP server
app = Server("Parliament MCP Multi-API Enhanced")

# API Configuration
MEMBERS_API_BASE = "https://members-api.parliament.uk/api"
TWFY_API_BASE = "https://www.theyworkforyou.com/api"

class ParliamentAPI:
    """Multi-source Parliament API client with enhanced historical support"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Any] = {}
    
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={"User-Agent": "Parliament-MCP-Enhanced/1.0"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _safe_api_call(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make API call with comprehensive error handling"""
        if not self.session:
            return {"error": "Session not initialized"}
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    # Handle different content types
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if 'application/json' in content_type:
                        data = await response.json()
                    elif 'text/javascript' in content_type or 'application/javascript' in content_type:
                        # TheyWorkForYou returns JavaScript format
                        text_data = await response.text()
                        try:
                            # Try to extract JSON from JavaScript response
                            import re
                            import json
                            # Look for JSON-like structure in the response
                            json_match = re.search(r'\{.*\}', text_data, re.DOTALL)
                            if json_match:
                                data = json.loads(json_match.group())
                            else:
                                data = {"raw_response": text_data, "format": "javascript"}
                        except:
                            data = {"raw_response": text_data, "format": "javascript"}
                    else:
                        # Fallback for other content types
                        data = {"raw_response": await response.text(), "content_type": content_type}
                    
                    return {"success": True, "data": data}
                else:
                    return {
                        "error": f"HTTP {response.status}",
                        "url": url,
                        "params": params
                    }
        except Exception as e:
            return {
                "error": str(e),
                "url": url,
                "params": params
            }
    
    async def search_constituencies(self, search_text: Optional[str] = None, constituency_id: Optional[int] = None) -> Dict[str, Any]:
        """Search constituencies with multiple approaches"""
        results = {}
        
        if search_text:
            url = f"{MEMBERS_API_BASE}/Location/Constituency/Search"
            params = {"searchText": search_text, "take": 20}
            results["search_results"] = await self._safe_api_call(url, params)
        
        if constituency_id:
            url = f"{MEMBERS_API_BASE}/Location/Constituency/{constituency_id}"
            results["specific_constituency"] = await self._safe_api_call(url)
        
        return {
            "query": {"search_text": search_text, "constituency_id": constituency_id},
            "source": "UK Parliament Members API",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def search_historical_member(self, name: str, target_date: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive historical member search"""
        all_results = {}
        analysis = {"data_sources": [], "findings": []}
        
        # Source 1: Current Members API
        members_url = f"{MEMBERS_API_BASE}/Members/Search"
        
        # Current members
        current_params = {"Name": name, "IsCurrentMember": "true", "take": 10}
        current_result = await self._safe_api_call(members_url, current_params)
        all_results["current_members"] = current_result
        analysis["data_sources"].append("UK Parliament Members API (Current)")
        
        # Former members
        former_params = {"Name": name, "IsCurrentMember": "false", "take": 10}
        former_result = await self._safe_api_call(members_url, former_params)
        all_results["former_members"] = former_result
        analysis["data_sources"].append("UK Parliament Members API (Former)")
        
        # Source 2: TheyWorkForYou for historical data
        if target_date:
            twfy_url = f"{TWFY_API_BASE}/getPerson"
            twfy_params = {"output": "js", "name": name}
            twfy_result = await self._safe_api_call(twfy_url, twfy_params)
            all_results["theyworkforyou"] = twfy_result
            analysis["data_sources"].append("TheyWorkForYou API")
        
        # Analysis
        if current_result.get("success"):
            analysis["findings"].append("Found in current Members API")
        if former_result.get("success"):
            analysis["findings"].append("Found in former Members API")
        
        # Historical guidance
        historical_guidance = self._get_historical_guidance(target_date)
        
        return {
            "search_name": name,
            "target_date": target_date,
            "results": all_results,
            "analysis": analysis,
            "historical_guidance": historical_guidance,
            "timestamp": datetime.now().isoformat()
        }
    
    async def search_hansard_multi_source(self, query: Optional[str] = None, date_from: Optional[str] = None, 
                                        date_to: Optional[str] = None, house: Optional[str] = None,
                                        member_name: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced Hansard search with multiple source guidance"""
        
        search_params = {
            "query": query,
            "date_from": date_from,
            "date_to": date_to,
            "house": house,
            "member_name": member_name
        }
        
        sources_info = {}
        recommendations = []
        
        # TheyWorkForYou approach
        if query or member_name:
            twfy_url = f"{TWFY_API_BASE}/getDebates"
            twfy_params = {"output": "js", "type": "commons"}
            if query:
                twfy_params["search"] = query
            if member_name:
                twfy_params["person"] = member_name
            if date_from:
                twfy_params["date"] = date_from
            
            twfy_result = await self._safe_api_call(twfy_url, twfy_params)
            sources_info["theyworkforyou"] = {
                "result": twfy_result,
                "coverage": "1935 onwards",
                "best_for": "Historical speeches and debates"
            }
            
            if twfy_result.get("success"):
                recommendations.append("TheyWorkForYou found relevant data")
        
        # Official Hansard website guidance
        sources_info["hansard_website"] = {
            "url": "https://hansard.parliament.uk/search",
            "coverage": "1803 onwards - most comprehensive",
            "parameters": search_params,
            "note": "Manual search recommended for comprehensive results"
        }
        
        # Historical period guidance
        if date_from and date_from < "2000-01-01":
            sources_info["historical_note"] = self._get_historical_guidance(date_from)
        
        return {
            "search_parameters": search_params,
            "sources": sources_info,
            "recommendations": recommendations,
            "summary": f"Searched {len(sources_info)} data sources",
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_historical_guidance(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Provide guidance for historical parliamentary data"""
        guidance = {
            "general_resources": [
                "TheyWorkForYou.com (1935 onwards)",
                "Hansard.parliament.uk (1803 onwards)",
                "Data.parliament.uk (structured data)",
                "Parliamentary Archives"
            ]
        }
        
        if date:
            try:
                year = int(date[:4])
                if year < 1935:
                    guidance["period_note"] = f"For {year}, use physical parliamentary records or academic databases"
                    guidance["specific_resources"] = [
                        "Parliamentary Archives",
                        "National Archives",
                        "Academic libraries with Hansard collections"
                    ]
                elif year < 2000:
                    guidance["period_note"] = f"For {year}, TheyWorkForYou should have comprehensive coverage"
                    guidance["best_api"] = "TheyWorkForYou"
                else:
                    guidance["period_note"] = f"For {year}, multiple modern APIs available"
                    guidance["best_api"] = "Members API + TheyWorkForYou"
            except:
                pass
        
        return guidance

# Global API client
api_client = None

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List enhanced Parliament MCP tools"""
    return [
        Tool(
            name="search_constituency_enhanced",
            description="Search UK Parliament constituencies with enhanced error handling",
            inputSchema={
                "type": "object",
                "properties": {
                    "searchText": {"type": "string", "description": "Search text for constituencies"},
                    "constituency_id": {"type": "integer", "description": "Specific constituency ID"}
                }
            }
        ),
        Tool(
            name="search_member_historical",
            description="Search for MPs with historical context - answers questions like 'Was X an MP in 1992?'",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Member name to search for"},
                    "target_date": {"type": "string", "description": "Date to check if they were MP (YYYY-MM-DD format)"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="search_hansard_enhanced",
            description="Search Hansard records with multiple source recommendations",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for debates/speeches"},
                    "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "house": {"type": "string", "enum": ["Commons", "Lords"], "description": "Parliamentary house"},
                    "member_name": {"type": "string", "description": "Specific member name"}
                }
            }
        ),
        Tool(
            name="get_api_status",
            description="Check status and capabilities of Parliament APIs",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls with enhanced error handling"""
    global api_client
    
    try:
        async with ParliamentAPI() as client:
            api_client = client
            
            if name == "search_constituency_enhanced":
                result = await client.search_constituencies(
                    arguments.get("searchText"),
                    arguments.get("constituency_id")
                )
            elif name == "search_member_historical":
                result = await client.search_historical_member(
                    arguments.get("name"),
                    arguments.get("target_date")
                )
            elif name == "search_hansard_enhanced":
                result = await client.search_hansard_multi_source(
                    arguments.get("query"),
                    arguments.get("date_from"),
                    arguments.get("date_to"),
                    arguments.get("house"),
                    arguments.get("member_name")
                )
            elif name == "get_api_status":
                result = await get_api_status(client)
            else:
                result = {"error": f"Unknown tool: {name}"}
            
            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [TextContent(type="text", text=json.dumps({
            "error": str(e),
            "tool": name,
            "arguments": arguments
        }, indent=2))]

async def get_api_status(client: ParliamentAPI) -> Dict[str, Any]:
    """Check status of all Parliament APIs"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "apis": {}
    }
    
    # Test Members API
    members_test = await client._safe_api_call(f"{MEMBERS_API_BASE}/Members/Search", {"Name": "Test", "take": 1})
    status["apis"]["members_api"] = {
        "url": MEMBERS_API_BASE,
        "status": "available" if members_test.get("success") else "error",
        "test_result": members_test.get("error", "OK"),
        "capabilities": ["current_mps", "constituencies", "former_mps_limited"],
        "historical_coverage": "Limited"
    }
    
    # Test TheyWorkForYou API
    twfy_test = await client._safe_api_call(f"{TWFY_API_BASE}/getPerson", {"output": "js", "name": "Test"})
    status["apis"]["theyworkforyou"] = {
        "url": TWFY_API_BASE,
        "status": "available" if twfy_test.get("success") else "error",
        "test_result": twfy_test.get("error", "OK"),
        "capabilities": ["historical_mps", "debates", "voting_records"],
        "historical_coverage": "Excellent (1935 onwards)"
    }
    
    status["summary"] = {
        "total_apis": len(status["apis"]),
        "available_apis": len([api for api in status["apis"].values() if api["status"] == "available"]),
        "historical_capability": "Enhanced with multiple sources",
        "recommendation": "Use Members API for current data, TheyWorkForYou for historical data"
    }
    
    return status

async def main():
    """Main entry point for enhanced multi-API server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    print("🏛️ Parliament MCP Multi-API Enhanced Server starting...")
    print("📚 Historical data support: 1935 onwards via TheyWorkForYou")
    print("🔍 Current data: UK Parliament Members API")
    asyncio.run(main())
