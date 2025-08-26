# Deep Research MCP Server - FastMCP Edition

A powerful Model Context Protocol (MCP) server built with modern FastMCP framework, designed for comprehensive web research and content analysis.

## Features

### Intelligent Search Engine
- **Google Grounding Search**: Uses Google official Grounding API for most accurate search results and citations
- **Multi-source Search**: Supports Google, Bing, DuckDuckGo as fallback options
- **Smart Query Generation**: Automatically generates and expands keyword queries
- **Relevance Scoring**: Automatic result ranking and deduplication

### Content Analysis
- Automatic content summarization
- Key point extraction
- Fact identification
- Quote extraction
- Statistical data analysis

### Research Reports
- Multi-format reports (Markdown, HTML, JSON)
- Structured research methodology
- Source citation management
- Executive summary generation

### Fact Checking
- Multi-source cross-verification
- Supporting/contradicting evidence analysis
- Credibility assessment

## Installation

1. Clone or download the project:
```bash
cd deep-research/
```

2. Install dependencies:
```bash
pip install -e .
```

Or using uv (recommended):
```bash
uv add fastmcp httpx beautifulsoup4 python-dotenv markdownify lxml pydantic google-generativeai
```

3. Copy environment configuration (optional):
```bash
cp .env.example .env
```

## Usage

### Running as MCP Server

```bash
uv run main.py
```

### Integration with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "deep-research": {
      "command": "uv",
      "args": ["run", "main.py"],
      "cwd": "/path/to/deep-research"
    }
  }
}
```

## Available Tools

### 1. start_research
Start a new deep research session

```json
{
  "topic": "AI applications in healthcare",
  "depth": "deep",
  "sources": ["web", "news"],
  "language": "en"
}
```

**Parameters:**
- `topic`: Research topic (required)
- `depth`: Research depth - "basic", "intermediate", "deep", "comprehensive"
- `sources`: Data sources - ["web", "news", "academic"]
- `language`: Language preference, default "en"

### 2. analyze_content
Analyze web content

```json
{
  "url": "https://example.com/article",
  "analysis_type": "summary"
}
```

**Analysis Types:**
- `summary`: Complete summary
- `key_points`: Key highlights
- `facts`: Facts and data
- `quotes`: Important quotes
- `statistics`: Statistical data

### 3. search_sources
Search multiple sources

```json
{
  "query": "machine learning trends 2024",
  "sources": ["google", "bing"],
  "limit": 10
}
```

### 4. generate_report
Generate research report

```json
{
  "session_id": "research_1",
  "format": "markdown",
  "sections": ["executive_summary", "key_findings", "sources", "conclusion"]
}
```

**Available Formats:**
- `markdown`: Markdown format
- `html`: HTML format
- `json`: JSON format

**Available Sections:**
- `executive_summary`: Executive summary
- `key_findings`: Key findings
- `search_results`: Search results summary
- `sources`: Data sources
- `methodology`: Research methodology
- `detailed_analysis`: Detailed analysis
- `limitations`: Research limitations
- `conclusion`: Conclusions

### 5. fact_check
Fact checking

```json
{
  "statement": "COVID-19 vaccines have over 90% effectiveness",
  "context": "Research on mRNA vaccines"
}
```

## Usage Examples

### Basic Research
```python
# Start research
start_research({
    "topic": "Blockchain applications in supply chain management",
    "depth": "intermediate",
    "sources": ["web", "news"]
})

# Generate report
generate_report({
    "session_id": "research_1",
    "format": "markdown"
})
```

### Content Analysis
```python
# Analyze specific webpage
analyze_content({
    "url": "https://arxiv.org/abs/2024.xxxxx",
    "analysis_type": "key_points"
})
```

### Fact Checking
```python
# Verify statement
fact_check({
    "statement": "OpenAI GPT-4 has 1.76 trillion parameters",
    "context": "Technical specifications of large language models"
})
```

## Configuration

### Environment Variables

#### Google Grounding Search API (Recommended)
- `GOOGLE_API_KEY`: Google Grounding API key
  - Get from: [Google AI Studio](https://aistudio.google.com/)
  - Function: Uses Google official Grounding search for most accurate results and citations

#### Fallback Search Engines
- `GOOGLE_CX`: Google Custom Search Engine ID (fallback use)
- `BING_SUBSCRIPTION_KEY`: Bing Search API key (optional)

#### Performance Settings
- `REQUEST_DELAY`: Request interval (seconds), default 1.0
- `MAX_CONCURRENT_REQUESTS`: Maximum concurrent requests, default 5
- `DEFAULT_TIMEOUT`: API timeout (seconds), default 30

### Research Depth Levels
- **basic**: Basic search, 3-5 queries
- **intermediate**: Intermediate search, 5-8 queries
- **deep**: Deep search, 7-10 queries
- **comprehensive**: Comprehensive search, 10+ queries

## Technical Architecture

### Core Modules
- **main.py**: MCP server main program
- **research_engine.py**: Research engine core
- **content_analyzer.py**: Content analysis module
- **report_generator.py**: Report generator

### Key Features
- **FastMCP Framework**: Uses modern FastMCP 2.0 for type safety and advanced features
- **Asynchronous Processing**: High-performance asyncio handling for multiple requests
- **Type Safety**: Pydantic models ensure parameter validation and IDE support
- **Context Awareness**: Built-in progress tracking
- **Multi-source Integration**: Supports multiple search engines and data sources
- **Intelligent Ranking**: Relevance-based result ranking and deduplication
- **Content Cleaning**: Automatic filtering and cleaning of web content
- **Rate Limiting**: Respects website crawling policies

## Limitations

### Technical Limitations
- Only accesses publicly available web content
- Primarily processes English content, limited support for other languages
- Depends on search engine algorithms for source discovery
- JavaScript-heavy websites may not be fully analyzed

### Content Analysis Limitations
- Automated processing, not manually curated
- May miss subtle nuances requiring domain expertise
- No manual verification of source credibility or accuracy
- Paywall and registration-protected content will be excluded

## Development

### Dependencies
- `fastmcp`: Modern MCP framework with type safety and advanced features
- `httpx`: High-performance asynchronous HTTP client
- `beautifulsoup4`: Powerful HTML parser
- `markdownify`: HTML to Markdown conversion tool
- `python-dotenv`: Environment variable management
- `pydantic`: Data validation and type safety
- `lxml`: High-performance XML/HTML processor
- `google-generativeai`: Google Grounding Search API client

### Contributing
1. Fork the project
2. Create feature branch
3. Commit changes
4. Create Pull Request

## License

MIT License

## Support & Feedback

If you encounter issues or have feature suggestions, please create an Issue or contact the development team.

---

**Note**: This tool is designed to assist research work. Please comply with relevant website terms of service and copyright regulations when using.