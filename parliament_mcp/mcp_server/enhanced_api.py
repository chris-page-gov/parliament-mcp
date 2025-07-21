"""
Enhanced MCP API with intelligent tool selection using MCP Sampling
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel

from parliament_mcp.mcp_server.handlers import (
    get_constituency, get_election_results, search_members, get_detailed_member_information,
    search_parliamentary_questions, search_debates, search_hansard_contributions,
    get_state_of_the_parties, get_government_posts, get_opposition_posts,
    get_departments
)
from parliament_mcp.mcp_server.intelligence import (
    intelligent_tool_selection, optimize_tool_parameters, evaluate_tool_results,
    QueryAnalysis, ToolRecommendation, QueryIntent
)

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp_server = FastMCP("Parliament MCP Server with Intelligence")


class IntelligentToolRequest(BaseModel):
    """Request for intelligent tool selection"""
    query: str
    context: Optional[Dict[str, Any]] = None
    auto_execute: bool = False
    evaluation_enabled: bool = True


class ToolExecutionResult(BaseModel):
    """Result of tool execution with intelligence metadata"""
    tool_name: str
    results: Any
    parameters_used: Dict[str, Any]
    confidence: float
    reasoning: str
    evaluation: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None


class IntelligentSearchResponse(BaseModel):
    """Response from intelligent search"""
    query_analysis: Dict[str, Any]
    recommended_tools: List[Dict[str, Any]]
    executed_results: Optional[List[ToolExecutionResult]] = None
    overall_assessment: Optional[str] = None


# Tool mapping for execution
TOOL_MAPPING = {
    "search_constituency": get_constituency,
    "get_election_results": get_election_results,
    "search_members": search_members,
    "get_detailed_member_information": get_detailed_member_information,
    "search_parliamentary_questions": search_parliamentary_questions,
    "search_debates": search_debates,
    "search_contributions": search_hansard_contributions,
    "get_state_of_the_parties": get_state_of_the_parties,
    "get_government_posts": get_government_posts,
    "get_opposition_posts": get_opposition_posts,
    "get_departments": get_departments
}


@mcp_server.tool()
async def intelligent_search(request: IntelligentToolRequest) -> IntelligentSearchResponse:
    """
    Intelligent search using MCP Sampling to determine the best tools and parameters.
    
    This tool analyzes the user's query using LLM reasoning to:
    1. Understand the intent and extract entities
    2. Recommend the most appropriate tools
    3. Optimize parameters for better results
    4. Optionally execute the tools and evaluate results
    
    Args:
        request: IntelligentToolRequest containing query and options
    
    Returns:
        IntelligentSearchResponse with analysis, recommendations, and optional results
    """
    try:
        logger.info(f"Intelligent search request: {request.query}")
        
        # Step 1: Analyze query and get tool recommendations
        analysis, recommendations = await intelligent_tool_selection(request.query, request.context)
        
        # Convert to serializable format
        query_analysis_dict = {
            "intent": analysis.intent.value,
            "entities": analysis.entities,
            "temporal_context": analysis.temporal_context,
            "geographic_context": analysis.geographic_context,
            "confidence": analysis.confidence,
            "keywords": analysis.keywords
        }
        
        recommendations_dict = []
        for rec in recommendations:
            recommendations_dict.append({
                "tool_name": rec.tool_name,
                "confidence": rec.confidence,
                "reasoning": rec.reasoning,
                "suggested_parameters": rec.suggested_parameters,
                "priority": rec.priority
            })
        
        response = IntelligentSearchResponse(
            query_analysis=query_analysis_dict,
            recommended_tools=recommendations_dict
        )
        
        # Step 2: Auto-execute if requested
        if request.auto_execute and recommendations:
            executed_results = []
            
            for rec in recommendations[:2]:  # Execute top 2 recommendations
                try:
                    # Get the tool function
                    tool_func = TOOL_MAPPING.get(rec.tool_name)
                    if not tool_func:
                        logger.warning(f"Tool {rec.tool_name} not found in mapping")
                        continue
                    
                    # Optimize parameters
                    optimized_params = await optimize_tool_parameters(
                        rec.tool_name, rec.suggested_parameters, analysis, request.query
                    )
                    
                    # Execute the tool
                    logger.info(f"Executing {rec.tool_name} with params: {optimized_params}")
                    
                    # Handle different parameter signatures
                    if rec.tool_name == "search_constituency":
                        results = await tool_func(
                            searchText=optimized_params.get("searchText"),
                            constituency_id=optimized_params.get("constituency_id"),
                            skip=optimized_params.get("skip", 0),
                            take=optimized_params.get("take", 10)
                        )
                    elif rec.tool_name == "search_members":
                        results = await tool_func(
                            Name=optimized_params.get("Name"),
                            PartyId=optimized_params.get("PartyId"),
                            House=optimized_params.get("House"),
                            ConstituencyId=optimized_params.get("ConstituencyId"),
                            Gender=optimized_params.get("Gender"),
                            member_since=optimized_params.get("member_since"),
                            member_until=optimized_params.get("member_until"),
                            IsCurrentMember=optimized_params.get("IsCurrentMember")
                        )
                    elif rec.tool_name == "search_debates":
                        results = await tool_func(
                            query=optimized_params.get("query"),
                            dateFrom=optimized_params.get("dateFrom"),
                            dateTo=optimized_params.get("dateTo"),
                            house=optimized_params.get("house"),
                            maxResults=optimized_params.get("maxResults", 10)
                        )
                    elif rec.tool_name == "search_contributions":
                        results = await tool_func(
                            query=optimized_params.get("query"),
                            memberId=optimized_params.get("memberId"),
                            dateFrom=optimized_params.get("dateFrom"),
                            dateTo=optimized_params.get("dateTo"),
                            debateId=optimized_params.get("debateId"),
                            house=optimized_params.get("house"),
                            maxResults=optimized_params.get("maxResults", 10)
                        )
                    elif rec.tool_name == "search_parliamentary_questions":
                        results = await tool_func(
                            query=optimized_params.get("query"),
                            dateFrom=optimized_params.get("dateFrom"),
                            dateTo=optimized_params.get("dateTo"),
                            party=optimized_params.get("party"),
                            member_name=optimized_params.get("member_name"),
                            member_id=optimized_params.get("member_id")
                        )
                    else:
                        # For tools with no parameters or simple signatures
                        results = await tool_func(**optimized_params)
                    
                    # Evaluate results if enabled
                    evaluation = None
                    if request.evaluation_enabled:
                        evaluation = await evaluate_tool_results(
                            request.query, rec.tool_name, results, analysis.intent
                        )
                    
                    # Create execution result
                    exec_result = ToolExecutionResult(
                        tool_name=rec.tool_name,
                        results=results,
                        parameters_used=optimized_params,
                        confidence=rec.confidence,
                        reasoning=rec.reasoning,
                        evaluation=evaluation
                    )
                    
                    executed_results.append(exec_result)
                    
                except Exception as e:
                    logger.error(f"Error executing tool {rec.tool_name}: {e}")
                    # Add error result
                    exec_result = ToolExecutionResult(
                        tool_name=rec.tool_name,
                        results={"error": str(e)},
                        parameters_used=rec.suggested_parameters,
                        confidence=rec.confidence,
                        reasoning=f"Execution failed: {str(e)}"
                    )
                    executed_results.append(exec_result)
            
            response.executed_results = executed_results
            
            # Generate overall assessment
            if executed_results and request.evaluation_enabled:
                total_quality = sum(r.evaluation.get("quality_score", 0.5) for r in executed_results if r.evaluation)
                avg_quality = total_quality / len([r for r in executed_results if r.evaluation])
                
                response.overall_assessment = f"Query executed with {len(executed_results)} tools. Average result quality: {avg_quality:.2f}"
        
        return response
        
    except Exception as e:
        logger.error(f"Intelligent search failed: {e}")
        return IntelligentSearchResponse(
            query_analysis={"error": str(e)},
            recommended_tools=[]
        )


@mcp_server.tool()
async def analyze_query_intent(query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze a query to understand user intent and extract entities.
    
    Args:
        query: The user's query text
        context: Optional context information
    
    Returns:
        Analysis results including intent, entities, and confidence
    """
    try:
        analysis, _ = await intelligent_tool_selection(query, context)
        
        return {
            "intent": analysis.intent.value,
            "entities": analysis.entities,
            "temporal_context": analysis.temporal_context,
            "geographic_context": analysis.geographic_context,
            "confidence": analysis.confidence,
            "keywords": analysis.keywords
        }
        
    except Exception as e:
        logger.error(f"Query analysis failed: {e}")
        return {"error": str(e)}


@mcp_server.tool()
async def get_tool_recommendations(query: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Get tool recommendations for a query without executing them.
    
    Args:
        query: The user's query text
        context: Optional context information
    
    Returns:
        List of recommended tools with reasoning and suggested parameters
    """
    try:
        _, recommendations = await intelligent_tool_selection(query, context)
        
        return [
            {
                "tool_name": rec.tool_name,
                "confidence": rec.confidence,
                "reasoning": rec.reasoning,
                "suggested_parameters": rec.suggested_parameters,
                "priority": rec.priority
            }
            for rec in recommendations
        ]
        
    except Exception as e:
        logger.error(f"Tool recommendation failed: {e}")
        return [{"error": str(e)}]


# Original tools - enhanced with intelligent defaults
@mcp_server.tool()
async def search_constituency(searchText: Optional[str] = None, constituency_id: Optional[int] = None, 
                            skip: int = 0, take: int = 10) -> Dict[str, Any]:
    """Search for constituencies by name or get comprehensive constituency details by ID"""
    return await get_constituency(searchText, constituency_id, skip, take)


@mcp_server.tool()
async def get_election_results(constituency_id: Optional[int] = None, election_id: Optional[int] = None, 
                             member_id: Optional[int] = None) -> Dict[str, Any]:
    """Get election results for constituencies or specific members"""
    return await get_election_results(constituency_id, election_id, member_id)


@mcp_server.tool()
async def search_members(Name: Optional[str] = None, PartyId: Optional[int] = None, 
                        House: Optional[str] = None, ConstituencyId: Optional[int] = None,
                        Gender: Optional[str] = None, member_since: Optional[str] = None,
                        member_until: Optional[str] = None, IsCurrentMember: Optional[bool] = None) -> Dict[str, Any]:
    """Search for members of the Commons or Lords by various criteria"""
    return await search_members(Name, PartyId, House, ConstituencyId, Gender, member_since, member_until, IsCurrentMember)


@mcp_server.tool()
async def get_detailed_member_information(member_id: int, include_synopsis: bool = True, 
                                        include_biography: bool = False, include_contact: bool = False,
                                        include_registered_interests: bool = False, include_voting_record: bool = False) -> Dict[str, Any]:
    """Get comprehensive member information including biography, contact, interests, and voting record"""
    return await get_detailed_member_information(member_id, include_synopsis, include_biography, 
                                                include_contact, include_registered_interests, include_voting_record)


@mcp_server.tool()
async def search_parliamentary_questions(query: Optional[str] = None, dateFrom: Optional[str] = None,
                                       dateTo: Optional[str] = None, party: Optional[str] = None,
                                       member_name: Optional[str] = None, member_id: Optional[int] = None) -> Dict[str, Any]:
    """Search Parliamentary Written Questions by topic, date, party, or member"""
    return await search_parliamentary_questions(query, dateFrom, dateTo, party, member_name, member_id)


@mcp_server.tool()
async def search_debates(query: Optional[str] = None, dateFrom: Optional[str] = None,
                        dateTo: Optional[str] = None, house: Optional[str] = None, 
                        maxResults: int = 10) -> Dict[str, Any]:
    """Search through debate titles to find relevant debates"""
    return await search_debates(query, dateFrom, dateTo, house, maxResults)


@mcp_server.tool()
async def search_contributions(query: Optional[str] = None, memberId: Optional[int] = None,
                             dateFrom: Optional[str] = None, dateTo: Optional[str] = None,
                             debateId: Optional[int] = None, house: Optional[str] = None,
                             maxResults: int = 10) -> Dict[str, Any]:
    """Search Hansard parliamentary records for actual spoken contributions during debates"""
    return await search_hansard_contributions(query, memberId, dateFrom, dateTo, debateId, house, maxResults)


@mcp_server.tool()
async def get_state_of_the_parties(house: str = "Commons", forDate: Optional[str] = None) -> Dict[str, Any]:
    """Get state of the parties for a house on a specific date"""
    return await get_state_of_the_parties(house, forDate)


@mcp_server.tool()
async def get_government_posts() -> Dict[str, Any]:
    """Get exhaustive list of all government posts and their current holders"""
    return await get_government_posts()


@mcp_server.tool()
async def get_opposition_posts() -> Dict[str, Any]:
    """Get exhaustive list of all opposition posts and their current holders"""
    return await get_opposition_posts()


@mcp_server.tool()
async def get_departments() -> Dict[str, Any]:
    """Get reference data for government departments"""
    return await get_departments()


if __name__ == "__main__":
    mcp_server.run()
