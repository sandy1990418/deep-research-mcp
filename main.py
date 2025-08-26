#!/usr/bin/env python3
"""
Deep Research MCP Server - Advanced web research and content analysis using FastMCP
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Literal
import os
from dotenv import load_dotenv

# FastMCP imports
from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

# Research functionality
from research_engine import ResearchEngine, ResearchConfig
from content_analyzer import ContentAnalyzer
from report_generator import ReportGenerator

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deep-research-mcp")

# Initialize FastMCP server
mcp = FastMCP("Deep Research 🔍", dependencies=["httpx", "beautifulsoup4", "markdownify"])

# Initialize components
research_engine = ResearchEngine()
content_analyzer = ContentAnalyzer()
report_generator = ReportGenerator()

# Store research sessions (in production, use database)
research_sessions: Dict[str, Dict[str, Any]] = {}

# Pydantic models for type safety
class ResearchRequest(BaseModel):
    topic: str = Field(description="Research topic or question")
    depth: Literal["basic", "intermediate", "deep", "comprehensive"] = Field(
        default="intermediate", 
        description="Research depth level"
    )
    sources: List[str] = Field(
        default=["web", "news"], 
        description="Preferred sources"
    )
    language: str = Field(default="en", description="Research language preference")

class ContentAnalysisRequest(BaseModel):
    url: str = Field(description="URL to analyze")
    analysis_type: Literal["summary", "key_points", "facts", "quotes", "statistics"] = Field(
        default="summary",
        description="Type of analysis to perform"
    )

class SearchRequest(BaseModel):
    query: str = Field(description="Search query")
    sources: List[str] = Field(
        default=["google"], 
        description="Sources to search"
    )
    limit: int = Field(default=10, description="Maximum number of results per source")

class ReportRequest(BaseModel):
    session_id: str = Field(description="Research session ID")
    format: Literal["markdown", "html", "json"] = Field(
        default="markdown",
        description="Report format"
    )
    sections: List[str] = Field(
        default=["executive_summary", "key_findings", "sources", "conclusion"],
        description="Sections to include in report"
    )

class FactCheckRequest(BaseModel):
    statement: str = Field(description="Statement to fact-check")
    context: str = Field(default="", description="Additional context")

# Resources
@mcp.resource("research://sessions")
def get_research_sessions() -> str:
    """Get current research sessions"""
    return str(research_sessions)

@mcp.resource("research://reports")
def get_research_reports() -> str:
    """Get generated research reports"""
    reports = []
    for session_id, session in research_sessions.items():
        if "report" in session:
            reports.append({
                "session_id": session_id,
                "topic": session.get("topic", "Unknown"),
                "report": session["report"]
            })
    return str(reports)

# Tools
@mcp.tool()
async def start_research(
    ctx: Context,
    request: ResearchRequest
) -> str:
    """
    Start a new deep research session on a given topic.
    
    This tool begins comprehensive research by:
    - Generating multiple search queries based on the topic
    - Searching across multiple sources (Google, Bing, etc.)
    - Analyzing and ranking results by relevance
    - Extracting key findings from top sources
    
    Returns a research session ID that can be used for report generation.
    """
    try:
        ctx.info(f"🔍 Starting research on: {request.topic}", extra={
            "topic": request.topic,
            "depth": request.depth, 
            "sources": request.sources,
            "language": request.language
        })
        
        # Generate unique session ID
        session_id = f"research_{len(research_sessions) + 1}"
        
        # Create research configuration
        config = ResearchConfig(
            topic=request.topic,
            depth=request.depth,
            sources=request.sources,
            language=request.language
        )
        
        # Initialize session
        session_data = {
            "session_id": session_id,
            "topic": request.topic,
            "config": config.dict(),
            "status": "started",
            "results": {},
            "sources_found": []
        }
        
        research_sessions[session_id] = session_data
        
        # Start research process
        ctx.info("🔍 Conducting multi-source research...", extra={
            "session_id": session_id,
            "queries_generated": len(config.sources)
        })
        
        initial_results = await research_engine.start_research(config)
        
        session_data["results"] = initial_results
        session_data["status"] = "completed"
        
        search_results_count = len(initial_results.get('search_results', {}))
        key_sources_count = len(initial_results.get('key_sources', []))
        findings_count = len(initial_results.get('key_findings', []))
        
        ctx.info("✅ Research completed successfully", extra={
            "session_id": session_id,
            "search_engines_used": search_results_count,
            "key_sources_found": key_sources_count,
            "key_findings_extracted": findings_count,
            "total_sources": initial_results.get('total_sources', 0)
        })
        
        return f"""✅ Research session started successfully!

**Session Details:**
- Session ID: `{session_id}`
- Topic: {request.topic}
- Depth: {request.depth}
- Sources: {', '.join(request.sources)}

**Results Summary:**
- Search engines used: {search_results_count}
- Key sources identified: {key_sources_count}
- Key findings extracted: {findings_count}
- Total sources analyzed: {initial_results.get('total_sources', 0)}

**Next Steps:**
Use `generate_report` with session ID `{session_id}` to create a comprehensive research report.
"""
        
    except Exception as e:
        ctx.error("❌ Research failed", extra={
            "session_id": session_id if 'session_id' in locals() else "unknown",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "topic": request.topic
        })
        
        if 'session_id' in locals() and session_id in research_sessions:
            research_sessions[session_id]["status"] = "error"
            research_sessions[session_id]["error"] = str(e)
        return f"❌ Research failed: {str(e)}"

@mcp.tool()
async def analyze_content(
    ctx: Context,
    request: ContentAnalysisRequest
) -> str:
    """
    Analyze and extract key information from web content.
    
    This tool performs detailed analysis of web pages including:
    - Content summarization
    - Key points extraction
    - Facts and statistics identification
    - Quote extraction
    - Statistical data analysis
    """
    try:
        ctx.info(f"Analyzing content from: {request.url}")
        
        analysis_result = await content_analyzer.analyze_url(
            request.url, 
            request.analysis_type
        )
        
        ctx.info("Content analysis completed")
        
        return f"""📊 **Content Analysis Results**

**URL:** {request.url}
**Analysis Type:** {request.analysis_type}

---

{analysis_result}
"""
        
    except Exception as e:
        ctx.error(f"Content analysis failed: {str(e)}")
        return f"❌ Analysis failed: {str(e)}"

@mcp.tool()
async def search_sources(
    ctx: Context,
    request: SearchRequest
) -> str:
    """
    Search for information from multiple sources.
    
    This tool searches across multiple search engines simultaneously:
    - Google search with relevance ranking
    - Bing search with result deduplication  
    - DuckDuckGo for privacy-focused results
    
    Results are ranked by relevance and deduplicated automatically.
    """
    try:
        ctx.info(f"Searching for: {request.query}")
        
        search_results = await research_engine.search_multiple_sources(
            request.query, 
            request.sources, 
            request.limit
        )
        
        total_results = sum(len(results) for results in search_results.values())
        ctx.info(f"Found {total_results} total results across {len(request.sources)} sources")
        
        # Format results
        result_text = f"""🔍 **Search Results for:** "{request.query}"

**Sources searched:** {', '.join(request.sources)}
**Total results:** {total_results}

"""
        
        for source, results in search_results.items():
            result_text += f"\n## 🔸 {source.upper()} Results ({len(results)} found)\n\n"
            
            for i, result in enumerate(results[:5], 1):  # Show top 5 from each source
                title = result.get('title', 'No title')
                url = result.get('url', 'No URL')
                snippet = result.get('snippet', 'No summary')
                relevance = result.get('relevance_score', 0.0)
                
                result_text += f"**{i}. {title}**\n"
                result_text += f"   • URL: {url}\n"
                result_text += f"   • Relevance: {relevance:.2f}\n"
                result_text += f"   • Summary: {snippet}\n\n"
        
        return result_text
        
    except Exception as e:
        ctx.error(f"Search failed: {str(e)}")
        return f"❌ Search failed: {str(e)}"

@mcp.tool()
async def generate_report(
    ctx: Context,
    request: ReportRequest
) -> str:
    """
    Generate a comprehensive research report.
    
    This tool creates detailed research reports including:
    - Executive summary with key statistics
    - Key findings from analyzed sources
    - Source bibliography and citations
    - Research methodology description
    - Limitations and conclusions
    
    Reports can be generated in Markdown, HTML, or JSON format.
    """
    try:
        if request.session_id not in research_sessions:
            return f"❌ Session `{request.session_id}` not found. Available sessions: {list(research_sessions.keys())}"
        
        session_data = research_sessions[request.session_id]
        
        ctx.info(f"Generating {request.format} report for session: {request.session_id}")
        
        report = await report_generator.generate_report(
            session_data, 
            request.format, 
            request.sections
        )
        
        # Store report in session
        session_data["report"] = report
        session_data["report_format"] = request.format
        
        ctx.info("Report generation completed")
        
        return f"""📋 **Research Report Generated**

**Session:** {request.session_id}
**Topic:** {session_data.get('topic', 'Unknown')}
**Format:** {request.format}
**Sections:** {', '.join(request.sections)}

---

{report}
"""
        
    except Exception as e:
        ctx.error(f"Report generation failed: {str(e)}")
        return f"❌ Report generation failed: {str(e)}"

@mcp.tool()
async def fact_check(
    ctx: Context,
    request: FactCheckRequest
) -> str:
    """
    Fact-check information against multiple sources.
    
    This tool verifies statements by:
    - Searching multiple sources for supporting evidence
    - Identifying contradicting information
    - Analyzing source credibility and relevance
    - Providing confidence assessment
    
    Returns detailed analysis with supporting/contradicting evidence.
    """
    try:
        ctx.info(f"Fact-checking statement: {request.statement[:100]}...")
        
        fact_check_result = await research_engine.fact_check(
            request.statement, 
            request.context
        )
        
        status = fact_check_result.get('status', 'Unknown')
        confidence = fact_check_result.get('confidence', 'Unknown')
        sources_count = len(fact_check_result.get('sources', []))
        
        ctx.info(f"Fact-check completed: {status} with {confidence} confidence ({sources_count} sources)")
        
        # Format supporting evidence
        supporting = fact_check_result.get('supporting_evidence', [])
        supporting_text = "\n".join([
            f"• **{ev['title']}** ({ev['source']})\n  {ev['evidence']}\n"
            for ev in supporting[:3]  # Top 3 supporting
        ]) if supporting else "No supporting evidence found"
        
        # Format contradicting evidence
        contradicting = fact_check_result.get('contradicting_evidence', [])
        contradicting_text = "\n".join([
            f"• **{ev['title']}** ({ev['source']})\n  {ev['evidence']}\n"
            for ev in contradicting[:3]  # Top 3 contradicting
        ]) if contradicting else "No contradicting evidence found"
        
        return f"""✅ **Fact-Check Results**

**Statement:** "{request.statement}"
**Context:** {request.context if request.context else "None provided"}

---

**📊 Verification Summary:**
• **Status:** {status}
• **Confidence Level:** {confidence}
• **Sources Checked:** {sources_count}
• **Supporting Evidence Found:** {len(supporting)}
• **Contradicting Evidence Found:** {len(contradicting)}

---

**✅ Supporting Evidence:**
{supporting_text}

**❌ Contradicting Evidence:**
{contradicting_text}

---

**📝 Assessment:**
Based on analysis of {sources_count} sources, this statement appears to be **{status}** with **{confidence}** confidence. 
{"Consider the contradicting evidence when making decisions." if contradicting else "The available evidence generally supports this statement."}
"""
        
    except Exception as e:
        ctx.error(f"Fact-check failed: {str(e)}")
        return f"❌ Fact-check failed: {str(e)}"

# Prompts for research guidance
@mcp.prompt("research-help")
def research_help_prompt() -> str:
    """Get help and examples for using the Deep Research MCP Server"""
    return """# Deep Research MCP Server Help

## Available Tools:

### 🔍 start_research
Start comprehensive research on any topic
- **Basic**: Quick overview (3-5 queries)
- **Intermediate**: Balanced analysis (5-8 queries) 
- **Deep**: Thorough investigation (7-10 queries)
- **Comprehensive**: Exhaustive research (10+ queries)

Example: Research AI ethics with intermediate depth

### 📊 analyze_content
Analyze specific web pages for:
- **summary**: Complete content overview
- **key_points**: Important takeaways
- **facts**: Statistical data and facts
- **quotes**: Notable statements
- **statistics**: Numerical insights

### 🌐 search_sources
Multi-source search across Google, Bing, DuckDuckGo
- Automatic relevance ranking
- Duplicate detection
- Configurable result limits

### 📋 generate_report
Create professional research reports:
- **Formats**: Markdown, HTML, JSON
- **Sections**: Executive summary, findings, sources, methodology, conclusions
- Professional citations and bibliography

### ✅ fact_check
Verify claims against multiple sources:
- Multi-source verification
- Confidence assessment
- Supporting/contradicting evidence analysis

## Usage Tips:
1. Start with `start_research` to get session ID
2. Use session ID with `generate_report` for comprehensive analysis
3. Combine `analyze_content` for specific source analysis
4. Use `fact_check` to verify specific claims

## Example Workflow:
1. `start_research` on "renewable energy trends 2024"
2. `analyze_content` on key articles found
3. `fact_check` specific claims from sources
4. `generate_report` with comprehensive sections
"""

if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()