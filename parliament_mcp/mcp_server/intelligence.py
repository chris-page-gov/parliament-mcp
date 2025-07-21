"""
MCP Sampling Intelligence for Parliament MCP Server
Implements intelligent tool selection and parameter optimization using LLM reasoning.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from openai import AsyncAzureOpenAI
from parliament_mcp.settings import settings

logger = logging.getLogger(__name__)


class QueryIntent(Enum):
    """Classification of user query intent"""
    CONSTITUENCY_SEARCH = "constituency_search"
    MEMBER_SEARCH = "member_search"
    POLICY_RESEARCH = "policy_research"
    DEBATE_ANALYSIS = "debate_analysis"
    VOTING_RECORD = "voting_record"
    ELECTION_DATA = "election_data"
    REFERENCE_DATA = "reference_data"
    UNKNOWN = "unknown"


@dataclass
class ToolRecommendation:
    """Represents a tool recommendation with reasoning"""
    tool_name: str
    confidence: float
    reasoning: str
    suggested_parameters: Dict[str, Any]
    priority: int


@dataclass
class QueryAnalysis:
    """Analysis of a user query"""
    intent: QueryIntent
    entities: List[str]
    temporal_context: Optional[str]
    geographic_context: Optional[str]
    confidence: float
    keywords: List[str]


@dataclass
class ParameterSuggestion:
    """Suggestion for parameter optimization"""
    parameter: str
    value: Any
    reasoning: str
    confidence: float


class MCPSamplingClient:
    """Client for intelligent tool selection using Azure OpenAI"""
    
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        )
        self.model = "gpt-4o"  # Using GPT-4 for reasoning
        
        # Available tools metadata
        self.available_tools = {
            "search_constituency": {
                "description": "Search for constituencies by name or get comprehensive constituency details by ID",
                "parameters": ["searchText", "constituency_id", "skip", "take"],
                "use_cases": ["finding constituency by name", "getting constituency details", "exploring geographic areas"]
            },
            "get_election_results": {
                "description": "Get election results for constituencies or specific members",
                "parameters": ["constituency_id", "election_id", "member_id"],
                "use_cases": ["election outcomes", "voting statistics", "electoral history"]
            },
            "search_members": {
                "description": "Search for members of the Commons or Lords by various criteria",
                "parameters": ["Name", "PartyId", "House", "ConstituencyId", "Gender", "member_since", "member_until", "IsCurrentMember"],
                "use_cases": ["finding MPs", "party analysis", "demographic research"]
            },
            "get_detailed_member_information": {
                "description": "Get comprehensive member information including biography, contact, interests, and voting record",
                "parameters": ["member_id", "include_synopsis", "include_biography", "include_contact", "include_registered_interests", "include_voting_record"],
                "use_cases": ["MP profiles", "biographical research", "conflict of interest analysis"]
            },
            "search_parliamentary_questions": {
                "description": "Search Parliamentary Written Questions by topic, date, party, or member",
                "parameters": ["query", "dateFrom", "dateTo", "party", "member_name", "member_id"],
                "use_cases": ["policy research", "accountability tracking", "issue analysis"]
            },
            "search_debates": {
                "description": "Search through debate titles to find relevant debates",
                "parameters": ["query", "dateFrom", "dateTo", "house", "maxResults"],
                "use_cases": ["legislative analysis", "debate discovery", "parliamentary proceedings"]
            },
            "search_contributions": {
                "description": "Search Hansard parliamentary records for actual spoken contributions during debates",
                "parameters": ["query", "memberId", "dateFrom", "dateTo", "debateId", "house", "maxResults"],
                "use_cases": ["speech analysis", "MP positions", "debate participation"]
            },
            "get_state_of_the_parties": {
                "description": "Get state of the parties for a house on a specific date",
                "parameters": ["house", "forDate"],
                "use_cases": ["party composition", "historical analysis", "political balance"]
            },
            "get_government_posts": {
                "description": "Get exhaustive list of all government posts and their current holders",
                "parameters": [],
                "use_cases": ["government structure", "ministerial roles", "executive analysis"]
            },
            "get_opposition_posts": {
                "description": "Get exhaustive list of all opposition posts and their current holders",
                "parameters": [],
                "use_cases": ["opposition structure", "shadow cabinet", "political organization"]
            },
            "get_departments": {
                "description": "Get reference data for government departments",
                "parameters": [],
                "use_cases": ["government structure", "departmental analysis", "administrative research"]
            }
        }

    async def analyze_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> QueryAnalysis:
        """Analyze user query to understand intent and extract entities"""
        
        prompt = f"""
        Analyze this user query for a UK Parliament research system:
        
        Query: "{query}"
        Context: {json.dumps(context or {}, indent=2)}
        
        Classify the query intent and extract key information:
        
        1. Intent classification (choose one):
           - constituency_search: Finding or researching constituencies
           - member_search: Finding or researching MPs/Lords
           - policy_research: Researching policies, issues, or government actions
           - debate_analysis: Analyzing parliamentary debates or speeches
           - voting_record: Researching voting patterns or records
           - election_data: Election results or electoral analysis
           - reference_data: Government structure or reference information
           - unknown: Cannot determine clear intent
        
        2. Extract entities:
           - Names of people, places, constituencies
           - Political parties
           - Dates or time periods
           - Topics or issues
        
        3. Determine temporal context:
           - Specific dates mentioned
           - Relative time references (recent, last year, etc.)
           - Default to current if not specified
        
        4. Geographic context:
           - Specific constituencies mentioned
           - Regions or areas
           - House (Commons/Lords) references
        
        5. Keywords for search optimization
        
        Return a JSON object with:
        {{
            "intent": "intent_category",
            "entities": ["entity1", "entity2"],
            "temporal_context": "time_reference_or_null",
            "geographic_context": "geographic_reference_or_null", 
            "confidence": 0.0-1.0,
            "keywords": ["keyword1", "keyword2"]
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return QueryAnalysis(
                intent=QueryIntent(result.get("intent", "unknown")),
                entities=result.get("entities", []),
                temporal_context=result.get("temporal_context"),
                geographic_context=result.get("geographic_context"),
                confidence=result.get("confidence", 0.5),
                keywords=result.get("keywords", [])
            )
            
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            return QueryAnalysis(
                intent=QueryIntent.UNKNOWN,
                entities=[],
                temporal_context=None,
                geographic_context=None,
                confidence=0.0,
                keywords=[]
            )

    async def recommend_tools(self, query_analysis: QueryAnalysis, query: str) -> List[ToolRecommendation]:
        """Recommend appropriate tools based on query analysis"""
        
        tools_info = json.dumps(self.available_tools, indent=2)
        
        prompt = f"""
        Based on this query analysis for a UK Parliament research system, recommend the most appropriate tools:
        
        Original Query: "{query}"
        
        Analysis:
        - Intent: {query_analysis.intent.value}
        - Entities: {query_analysis.entities}
        - Temporal Context: {query_analysis.temporal_context}
        - Geographic Context: {query_analysis.geographic_context}
        - Keywords: {query_analysis.keywords}
        - Confidence: {query_analysis.confidence}
        
        Available Tools:
        {tools_info}
        
        Recommend 1-3 tools in priority order that would best fulfill this query. Consider:
        1. Direct relevance to the intent
        2. Ability to handle the extracted entities
        3. Temporal and geographic context
        4. Likelihood of returning useful results
        
        For each recommended tool, suggest optimal parameters based on the query analysis.
        
        Return a JSON array of recommendations:
        [
            {{
                "tool_name": "tool_name",
                "confidence": 0.0-1.0,
                "reasoning": "why this tool is recommended",
                "suggested_parameters": {{
                    "param1": "value1",
                    "param2": "value2"
                }},
                "priority": 1
            }}
        ]
        
        Focus on tools that will give the user the most relevant and comprehensive results.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            
            recommendations = []
            for item in result:
                recommendations.append(ToolRecommendation(
                    tool_name=item.get("tool_name"),
                    confidence=item.get("confidence", 0.5),
                    reasoning=item.get("reasoning", ""),
                    suggested_parameters=item.get("suggested_parameters", {}),
                    priority=item.get("priority", 999)
                ))
            
            # Sort by priority
            recommendations.sort(key=lambda x: x.priority)
            return recommendations
            
        except Exception as e:
            logger.error(f"Tool recommendation failed: {e}")
            return []

    async def optimize_parameters(self, tool_name: str, base_params: Dict[str, Any], 
                                query_analysis: QueryAnalysis, query: str) -> List[ParameterSuggestion]:
        """Optimize parameters for a specific tool call"""
        
        tool_info = self.available_tools.get(tool_name, {})
        
        prompt = f"""
        Optimize parameters for the '{tool_name}' tool based on this query analysis:
        
        Original Query: "{query}"
        Tool: {tool_name}
        Tool Description: {tool_info.get('description', '')}
        Available Parameters: {tool_info.get('parameters', [])}
        Current Parameters: {json.dumps(base_params, indent=2)}
        
        Query Analysis:
        - Intent: {query_analysis.intent.value}
        - Entities: {query_analysis.entities}
        - Temporal Context: {query_analysis.temporal_context}
        - Geographic Context: {query_analysis.geographic_context}
        - Keywords: {query_analysis.keywords}
        
        Suggest parameter optimizations to improve results:
        1. Date ranges based on temporal context
        2. Geographic filters based on location mentions
        3. Result limits based on query scope
        4. Search terms based on entities and keywords
        5. Boolean flags for comprehensive vs. focused results
        
        Consider current date: {datetime.now().strftime('%Y-%m-%d')}
        
        Return JSON array of parameter suggestions:
        [
            {{
                "parameter": "parameter_name",
                "value": "suggested_value",
                "reasoning": "why this optimization helps",
                "confidence": 0.0-1.0
            }}
        ]
        
        Only suggest parameters that would meaningfully improve the results.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            result = json.loads(response.choices[0].message.content)
            
            suggestions = []
            for item in result:
                suggestions.append(ParameterSuggestion(
                    parameter=item.get("parameter"),
                    value=item.get("value"),
                    reasoning=item.get("reasoning", ""),
                    confidence=item.get("confidence", 0.5)
                ))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Parameter optimization failed: {e}")
            return []

    async def evaluate_results(self, query: str, tool_name: str, results: Any, 
                             expected_intent: QueryIntent) -> Dict[str, Any]:
        """Evaluate the quality of results and suggest refinements"""
        
        # Convert results to string for analysis
        results_str = json.dumps(results, default=str, indent=2)[:2000]  # Limit size
        
        prompt = f"""
        Evaluate the quality of these search results for the user's query:
        
        Original Query: "{query}"
        Expected Intent: {expected_intent.value}
        Tool Used: {tool_name}
        
        Results (truncated):
        {results_str}
        
        Evaluate:
        1. Result quality (0.0-1.0): How well do results match the query intent?
        2. Result completeness: Are results comprehensive enough?
        3. Refinement suggestions: How could the search be improved?
        
        Consider:
        - Number of results returned
        - Relevance to the original query
        - Whether additional tools might provide better results
        - Parameter adjustments that could improve results
        
        Return JSON:
        {{
            "quality_score": 0.0-1.0,
            "completeness_score": 0.0-1.0,
            "result_count": number_of_results,
            "refinement_suggestions": [
                {{
                    "type": "parameter_adjustment|additional_tool|query_refinement",
                    "suggestion": "specific suggestion",
                    "reasoning": "why this would help"
                }}
            ],
            "overall_assessment": "brief summary of result quality"
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=600
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Result evaluation failed: {e}")
            return {
                "quality_score": 0.5,
                "completeness_score": 0.5,
                "result_count": 0,
                "refinement_suggestions": [],
                "overall_assessment": "Evaluation failed"
            }


# Global instance
sampling_client = MCPSamplingClient()


async def intelligent_tool_selection(query: str, context: Optional[Dict[str, Any]] = None) -> Tuple[QueryAnalysis, List[ToolRecommendation]]:
    """Main function for intelligent tool selection"""
    
    # Analyze the query
    analysis = await sampling_client.analyze_query(query, context)
    
    # Get tool recommendations
    recommendations = await sampling_client.recommend_tools(analysis, query)
    
    logger.info(f"Query analysis: Intent={analysis.intent.value}, Confidence={analysis.confidence}")
    logger.info(f"Tool recommendations: {[r.tool_name for r in recommendations]}")
    
    return analysis, recommendations


async def optimize_tool_parameters(tool_name: str, base_params: Dict[str, Any], 
                                 analysis: QueryAnalysis, query: str) -> Dict[str, Any]:
    """Optimize parameters for a tool call"""
    
    suggestions = await sampling_client.optimize_parameters(tool_name, base_params, analysis, query)
    
    # Apply suggestions with confidence threshold
    optimized_params = base_params.copy()
    for suggestion in suggestions:
        if suggestion.confidence > 0.7:  # Only apply high-confidence suggestions
            optimized_params[suggestion.parameter] = suggestion.value
            logger.info(f"Parameter optimization: {suggestion.parameter}={suggestion.value} ({suggestion.reasoning})")
    
    return optimized_params


async def evaluate_tool_results(query: str, tool_name: str, results: Any, 
                              expected_intent: QueryIntent) -> Dict[str, Any]:
    """Evaluate the quality of tool results"""
    
    evaluation = await sampling_client.evaluate_results(query, tool_name, results, expected_intent)
    
    logger.info(f"Result evaluation: Quality={evaluation.get('quality_score')}, Completeness={evaluation.get('completeness_score')}")
    
    return evaluation
