"""
Search and analyze prompt for Alfresco MCP Server.
Self-contained prompt for generating comprehensive search and analysis workflows.
"""


async def search_and_analyze_impl(query: str, analysis_type: str = "summary") -> str:
    """Generate comprehensive search and analysis prompts for Alfresco documents.
    
    Args:
        query: Search query for documents
        analysis_type: Type of analysis (summary, detailed, trends, compliance)
    
    Returns:
        Formatted prompt for document analysis workflow
    """
    base_prompt = f"""**Alfresco Document Analysis Request**

Please search for documents matching "{query}" and provide a {analysis_type} analysis.

**Step 1: Search**
Use the `search_content` tool to find relevant documents.

**Step 2: Analysis**
Based on the search results, provide:
"""
    
    if analysis_type == "summary":
        base_prompt += """
- Document count and types
- Key themes and topics
- Most relevant documents
- Quick insights
"""
    elif analysis_type == "detailed":
        base_prompt += """
- Comprehensive document inventory
- Metadata analysis (dates, authors, sizes)
- Content categorization
- Compliance status
- Recommended actions
- Related search suggestions
"""
    elif analysis_type == "trends":
        base_prompt += """
- Temporal patterns (creation/modification dates)
- Document lifecycle analysis
- Usage and access patterns
- Version history insights
- Storage optimization recommendations
"""
    elif analysis_type == "compliance":
        base_prompt += """
- Document retention analysis
- Security classification review
- Access permissions audit
- Regulatory compliance status
- Risk assessment
- Remediation recommendations
"""
    
    base_prompt += f"""
**Step 3: Recommendations**
Provide actionable insights and next steps based on the {analysis_type} analysis.
"""
    
    return base_prompt 