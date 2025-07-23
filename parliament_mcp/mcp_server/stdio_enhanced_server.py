#!/usr/bin/env python3
"""
Enhanced stdio-compatible Parliament MCP server with MCP Sampling intelligence.
This provides intelligent tool selection using Azure OpenAI for better query handling.
"""

import asyncio
import logging
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from typing import Any, Dict, List, Optional

# Configure logging to avoid stderr output that confuses VS Code
logging.basicConfig(level=logging.WARNING)

# Import Parliament MCP components
from parliament_mcp.settings import settings

# Try to import intelligence features
intelligence_available = False
try:
    from parliament_mcp.mcp_server.intelligence import (
        intelligent_tool_selection, 
        optimize_tool_parameters,
        evaluate_tool_results,
        QueryAnalysis,
        ToolRecommendation
    )
    intelligence_available = True
    print("🧠 Intelligence features loaded - MCP Sampling enabled", file=sys.stderr)
except ImportError as e:
    intelligence_available = False
    print(f"⚡ Intelligence features not available: {e}", file=sys.stderr)

# Import Parliament MCP utilities for API calls and Elasticsearch handlers
from parliament_mcp.mcp_server.utils import request_members_api, sanitize_params
from parliament_mcp.mcp_server.handlers import search_hansard_contributions
from parliament_mcp.elasticsearch_helpers import get_async_es_client

import sys

# Create the MCP server
app = Server("Parliament MCP Server Enhanced")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    tools = [
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
                        "enum": ["Commons", "Lords"],
                        "description": "House of Parliament (Commons or Lords)"
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
    
    # Add intelligent search tool if available
    if intelligence_available:
        tools.append(
            Tool(
                name="intelligent_search",
                description="Intelligent search using MCP Sampling to automatically select the best tools and parameters for your query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Your question or search query about UK Parliament"
                        },
                        "auto_execute": {
                            "type": "boolean",
                            "description": "Whether to automatically execute recommended tools",
                            "default": True
                        },
                        "max_tools": {
                            "type": "integer",
                            "description": "Maximum number of tools to execute",
                            "default": 3
                        }
                    },
                    "required": ["query"]
                }
            )
        )
    
    return tools

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    if name == "search_constituency":
        # Handle constituency search
        search_text = arguments.get("searchText")
        constituency_id = arguments.get("constituency_id")
        skip = arguments.get("skip", 0)
        take = arguments.get("take", 5)
        
        try:
            # Sanitize parameters
            params = sanitize_params(
                searchText=search_text,
                constituency_id=constituency_id,
                skip=skip,
                take=take
            )
            
            # Handle constituency search or details
            if search_text is not None:
                result = await request_members_api("/api/Location/Constituency/Search", params)
            elif constituency_id is not None:
                # Get constituency details
                result = await request_members_api(f"/api/Location/Constituency/{constituency_id}", {})
            else:
                return [TextContent(type="text", text="Error: Must provide either searchText or constituency_id")]
                
            return [TextContent(type="text", text=str(result))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error searching constituencies: {str(e)}")]
    
    elif name == "search_hansard":
        # Handle Hansard search
        query = arguments.get("query")
        house = arguments.get("house")
        date_from = arguments.get("date_from")
        date_to = arguments.get("date_to")
        skip = arguments.get("skip", 0)
        take = arguments.get("take", 5)
        
        try:
            # Use Elasticsearch for Hansard search
            async with get_async_es_client(settings) as es_client:
                result = await search_hansard_contributions(
                    es_client=es_client,
                    index=settings.HANSARD_CONTRIBUTIONS_INDEX,
                    query=query,
                    memberId=None,  # Could extend to support member filtering
                    dateFrom=date_from,
                    dateTo=date_to,
                    debateId=None,
                    house=house,
                    maxResults=take if take <= 100 else 100
                )
                
            return [TextContent(type="text", text=str(result))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error searching Hansard: {str(e)}")]
    
    elif name == "intelligent_search" and intelligence_available:
        # Handle intelligent search with MCP Sampling
        query = arguments.get("query")
        auto_execute = arguments.get("auto_execute", True)
        max_tools = arguments.get("max_tools", 3)
        
        try:
            # Step 1: Get intelligent tool recommendations
            analysis, recommendations = await intelligent_tool_selection(query, {})
            
            response = {
                "query_analysis": {
                    "intent": analysis.intent.value,
                    "entities": analysis.entities,
                    "temporal_context": analysis.temporal_context,
                    "geographic_context": analysis.geographic_context,
                    "confidence": analysis.confidence,
                    "keywords": analysis.keywords
                },
                "recommended_tools": []
            }
            
            # Add tool recommendations
            for rec in recommendations[:max_tools]:
                response["recommended_tools"].append({
                    "tool_name": rec.tool_name,
                    "confidence": rec.confidence,
                    "reasoning": rec.reasoning,
                    "suggested_parameters": rec.suggested_parameters,
                    "priority": rec.priority
                })
            
            # Step 2: Auto-execute if requested
            if auto_execute:
                executed_results = []
                for rec in recommendations[:max_tools]:
                    try:
                        # Map tool names to actual functions
                        if rec.tool_name == "search_constituency":
                            result = await get_constituency(**rec.suggested_parameters)
                        elif rec.tool_name == "search_hansard":
                            result = await search_hansard_contributions(**rec.suggested_parameters)
                        else:
                            continue
                            
                        # Evaluate results if possible
                        evaluation = None
                        try:
                            evaluation = await evaluate_tool_results([result], query, analysis)
                        except:
                            pass
                        
                        executed_results.append({
                            "tool_name": rec.tool_name,
                            "results": result,
                            "parameters_used": rec.suggested_parameters,
                            "confidence": rec.confidence,
                            "reasoning": rec.reasoning,
                            "evaluation": evaluation
                        })
                    except Exception as e:
                        executed_results.append({
                            "tool_name": rec.tool_name,
                            "error": str(e),
                            "parameters_used": rec.suggested_parameters
                        })
                
                response["executed_results"] = executed_results
            
            return [TextContent(type="text", text=str(response))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error in intelligent search: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Main entry point for the stdio server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
