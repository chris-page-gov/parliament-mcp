# Example: Using the Enhanced Parliament MCP Server

## Historical Member Query Example

Here's how the enhanced server handles the question "Was Tim Eggar an MP in March 1992?":

### Using the MCP Tools

```json
{
  "tool": "search_member_historical",
  "arguments": {
    "name": "Tim Eggar",
    "target_date": "1992-03-01"
  }
}
```

### Expected Response

```json
{
  "search_name": "Tim Eggar",
  "target_date": "1992-03-01",
  "results": {
    "current_members": {
      "success": true,
      "data": []
    },
    "former_members": {
      "success": true,
      "data": [...]
    },
    "theyworkforyou": {
      "success": false,
      "error": "Rate limited or API access issue"
    }
  },
  "analysis": {
    "data_sources": [
      "UK Parliament Members API (Current)",
      "UK Parliament Members API (Former)",
      "TheyWorkForYou API"
    ],
    "findings": [
      "Found in former Members API"
    ]
  },
  "historical_guidance": {
    "period_note": "For 1992, TheyWorkForYou should have comprehensive coverage",
    "best_api": "TheyWorkForYou",
    "general_resources": [
      "TheyWorkForYou.com (1935 onwards)",
      "Hansard.parliament.uk (1803 onwards)",
      "Data.parliament.uk (structured data)",
      "Parliamentary Archives"
    ]
  }
}
```

## Key Improvements Over Previous Implementation

### 1. Multiple Data Sources
- **Before:** Single Elasticsearch dependency (often unavailable)
- **After:** UK Parliament API + TheyWorkForYou + Hansard guidance

### 2. Historical Coverage
- **Before:** Limited to available Elasticsearch data
- **After:** 1935 onwards via TheyWorkForYou, guidance for earlier periods

### 3. Error Handling
- **Before:** "Connection error" when Elasticsearch down
- **After:** Graceful fallback, alternative suggestions, clear guidance

### 4. User Experience
- **Before:** Technical error messages
- **After:** Helpful recommendations, multiple options, context

### 5. Production Readiness
- **Before:** Development prototype
- **After:** Type safety, rate limiting, caching, comprehensive error handling

## Usage in VS Code

1. **Restart VS Code** to pick up the new MCP configuration
2. **Use the enhanced tools** in chat:
   - "Search for Tim Eggar as an MP in 1992"
   - "Find London constituencies" 
   - "Search Hansard for budget speeches in 1992"
3. **Get comprehensive results** with multiple data sources and guidance

## Alternative Access Methods

If the MCP integration isn't working, you can also:

1. **Run the server directly:**
   ```bash
   /workspace/.venv/bin/python -m parliament_mcp.mcp_server.multi_api_enhanced
   ```

2. **Use the HTTP server** (for web access):
   ```bash
   /workspace/.venv/bin/python -m parliament_mcp.mcp_server.main
   ```

3. **Manual API access** with the guidance provided by the server

## Benefits of This Implementation

- ✅ **Solves the historical data problem** identified in testing
- ✅ **Production-ready** with proper error handling
- ✅ **Multiple fallback options** when APIs are unavailable  
- ✅ **Clear guidance** for users on where to find historical data
- ✅ **Scalable architecture** for adding more data sources
- ✅ **Smart caching** to improve performance
