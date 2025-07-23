#!/usr/bin/env python3
"""
Stdio-compatible Parliament MCP server using standard MCP SDK.
This provides a stdio interface that VS Code can use directly.
"""

import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from typing import Any

# Configure logging to avoid stderr output that confuses VS Code
logging.basicConfig(level=logging.WARNING)

# Import Parliament MCP components
from parliament_mcp.settings import settings
from parliament_mcp.elasticsearch_helpers import get_async_es_client

# Create the MCP server
app = Server("Parliament MCP Server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="search_constituency",
            description="Search for UK Parliament constituencies by name or get details by constituency ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "searchText": {
                        "type": "string",
                        "description": "Search text for finding constituencies by name"
                    },
                    "constituency_id": {
                        "type": "integer",
                        "description": "Specific constituency ID to get detailed information"
                    },
                    "skip": {
                        "type": "integer", 
                        "description": "Number of results to skip for pagination",
                        "default": 0
                    },
                    "take": {
                        "type": "integer",
                        "description": "Number of results to return (max 20)",
                        "default": 5
                    }
                }
            }
        ),
        Tool(
            name="search_hansard",
            description="Search Hansard (Parliamentary debates and proceedings)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Hansard content"
                    },
                    "house": {
                        "type": "string",
                        "description": "House of Parliament (Commons or Lords)",
                        "enum": ["Commons", "Lords"]
                    },
                    "date_from": {
                        "type": "string",
                        "description": "Start date for search (YYYY-MM-DD format)"
                    },
                    "date_to": {
                        "type": "string", 
                        "description": "End date for search (YYYY-MM-DD format)"
                    },
                    "skip": {
                        "type": "integer",
                        "description": "Number of results to skip for pagination",
                        "default": 0
                    },
                    "take": {
                        "type": "integer",
                        "description": "Number of results to return (max 20)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls"""
    
    if name == "search_constituency":
        try:
            # Extract arguments
            search_text = arguments.get("searchText")
            constituency_id = arguments.get("constituency_id")
            skip = arguments.get("skip", 0)
            take = min(arguments.get("take", 5), 20)  # Limit to 20
            
            # Use Elasticsearch client
            async with get_async_es_client(settings) as es_client:
                if constituency_id:
                    # Get specific constituency by ID
                    query = {
                        "query": {"term": {"ConstituencyId": constituency_id}},
                        "_source": ["ConstituencyName", "ConstituencyId", "MPs", "ElectionResults"]
                    }
                else:
                    # Search constituencies by text
                    query = {
                        "query": {
                            "multi_match": {
                                "query": search_text or "",
                                "fields": ["ConstituencyName^2", "MPs.Name", "Location"]
                            }
                        },
                        "from": skip,
                        "size": take,
                        "_source": ["ConstituencyName", "ConstituencyId", "MPs.Name", "Location"]
                    }
                
                # Execute search
                result = await es_client.search(
                    index=settings.CONSTITUENCIES_INDEX or "constituencies",
                    body=query
                )
                
                # Format results
                hits = result.get("hits", {}).get("hits", [])
                if not hits:
                    return [TextContent(
                        type="text", 
                        text="No constituencies found matching your search criteria."
                    )]
                
                formatted_results = []
                for hit in hits:
                    source = hit["_source"]
                    formatted_results.append(f"**{source.get('ConstituencyName', 'Unknown')}** (ID: {source.get('ConstituencyId', 'N/A')})")
                    if "MPs" in source and source["MPs"]:
                        mp_names = [mp.get("Name", "Unknown") for mp in source["MPs"]]
                        formatted_results.append(f"  MPs: {', '.join(mp_names)}")
                    if "Location" in source:
                        formatted_results.append(f"  Location: {source['Location']}")
                    formatted_results.append("")
                
                return [TextContent(
                    type="text",
                    text=f"Found {len(hits)} constituency/constituencies:\n\n" + "\n".join(formatted_results)
                )]
                
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error searching constituencies: {str(e)}\n\nNote: This requires Elasticsearch to be running and configured."
            )]
    
    elif name == "search_hansard":
        try:
            # Extract arguments
            query_text = arguments.get("query", "")
            house = arguments.get("house")
            date_from = arguments.get("date_from")
            date_to = arguments.get("date_to")
            skip = arguments.get("skip", 0)
            take = min(arguments.get("take", 5), 20)
            
            if not query_text:
                return [TextContent(type="text", text="Query parameter is required for Hansard search.")]
            
            # Build Elasticsearch query
            must_clauses = [
                {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["Content^2", "Speaker", "Subject"]
                    }
                }
            ]
            
            # Add filters
            filters = []
            if house:
                filters.append({"term": {"House.keyword": house}})
            
            if date_from or date_to:
                date_range = {"range": {"SittingDate": {}}}
                if date_from:
                    date_range["range"]["SittingDate"]["gte"] = date_from
                if date_to:
                    date_range["range"]["SittingDate"]["lte"] = date_to
                filters.append(date_range)
            
            # Build final query
            es_query = {
                "query": {
                    "bool": {
                        "must": must_clauses,
                        "filter": filters
                    }
                },
                "from": skip,
                "size": take,
                "_source": ["Content", "Speaker", "SittingDate", "House", "Subject"],
                "sort": [{"SittingDate": {"order": "desc"}}]
            }
            
            # Execute search
            async with get_async_es_client(settings) as es_client:
                result = await es_client.search(
                    index=settings.HANSARD_CONTRIBUTIONS_INDEX or "hansard",
                    body=es_query
                )
                
                # Format results
                hits = result.get("hits", {}).get("hits", [])
                if not hits:
                    return [TextContent(
                        type="text",
                        text="No Hansard entries found matching your search criteria."
                    )]
                
                formatted_results = []
                for hit in hits:
                    source = hit["_source"]
                    formatted_results.append(f"**{source.get('SittingDate', 'Unknown Date')} - {source.get('House', 'Unknown House')}**")
                    if source.get("Speaker"):
                        formatted_results.append(f"Speaker: {source['Speaker']}")
                    if source.get("Subject"):
                        formatted_results.append(f"Subject: {source['Subject']}")
                    
                    content = source.get("Content", "")
                    if len(content) > 300:
                        content = content[:300] + "..."
                    formatted_results.append(f"Content: {content}")
                    formatted_results.append("---")
                
                return [TextContent(
                    type="text",
                    text=f"Found {len(hits)} Hansard entries:\n\n" + "\n".join(formatted_results)
                )]
                
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error searching Hansard: {str(e)}\n\nNote: This requires Elasticsearch to be running and configured."
            )]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Main entry point for stdio server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
