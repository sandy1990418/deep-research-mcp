#!/usr/bin/env python3
"""
Deep Research MCP Server - Usage Examples with FastMCP
"""

import asyncio
import json

def demo_fastmcp_tools():
    """Demonstrate FastMCP tool definitions and usage"""
    print("🔍 Deep Research MCP Server with FastMCP")
    print("=" * 60)
    
    tools_examples = {
        "start_research": {
            "description": "Start a new deep research session on a given topic",
            "features": [
                "Multi-source search (Google, Bing, DuckDuckGo)",
                "Intelligent query generation and expansion", 
                "Relevance-based result ranking",
                "Key findings extraction from top sources"
            ],
            "parameters": {
                "topic": "Research topic or question (required)",
                "depth": "basic | intermediate | deep | comprehensive",
                "sources": "List of sources: [\"web\", \"news\", \"academic\"]",
                "language": "Language preference (default: \"en\")"
            },
            "examples": [
                {
                    "name": "AI Ethics Research",
                    "request": {
                        "topic": "artificial intelligence ethics in healthcare",
                        "depth": "deep",
                        "sources": ["web", "news"],
                        "language": "en"
                    },
                    "expected_output": "Research session with 15+ sources, 5-8 key findings"
                },
                {
                    "name": "Climate Change Trends", 
                    "request": {
                        "topic": "climate change impacts 2024",
                        "depth": "comprehensive",
                        "sources": ["web", "news", "academic"]
                    },
                    "expected_output": "Exhaustive analysis with 20+ sources"
                },
                {
                    "name": "Quick Tech Overview",
                    "request": {
                        "topic": "quantum computing applications",
                        "depth": "basic"
                    },
                    "expected_output": "Basic overview with 5-8 sources"
                }
            ]
        },
        
        "analyze_content": {
            "description": "Analyze and extract key information from web content",
            "features": [
                "Automatic content summarization",
                "Key points extraction",
                "Facts and statistics identification",
                "Quote extraction with context",
                "Multi-format content processing"
            ],
            "parameters": {
                "url": "URL to analyze (required)",
                "analysis_type": "summary | key_points | facts | quotes | statistics"
            },
            "examples": [
                {
                    "name": "Research Paper Analysis",
                    "request": {
                        "url": "https://arxiv.org/abs/2023.12345",
                        "analysis_type": "key_points"
                    },
                    "expected_output": "Structured key points from academic paper"
                },
                {
                    "name": "News Article Summary",
                    "request": {
                        "url": "https://example.com/news-article",
                        "analysis_type": "summary"
                    },
                    "expected_output": "Comprehensive article summary with metadata"
                },
                {
                    "name": "Statistical Data Extraction",
                    "request": {
                        "url": "https://example.com/data-report", 
                        "analysis_type": "statistics"
                    },
                    "expected_output": "Extracted numerical data and trends"
                }
            ]
        },
        
        "search_sources": {
            "description": "Search for information from multiple sources simultaneously",
            "features": [
                "Multi-engine search (Google, Bing, DuckDuckGo)",
                "Automatic result deduplication",
                "Relevance scoring and ranking",
                "Configurable result limits per source"
            ],
            "parameters": {
                "query": "Search query (required)",
                "sources": "[\"google\", \"bing\", \"duckduckgo\"]",
                "limit": "Maximum results per source (default: 10)"
            },
            "examples": [
                {
                    "name": "Technology Trends Search",
                    "request": {
                        "query": "machine learning trends 2024",
                        "sources": ["google", "bing"],
                        "limit": 15
                    },
                    "expected_output": "30 ranked results from 2 sources"
                },
                {
                    "name": "Academic Research Search",
                    "request": {
                        "query": "renewable energy efficiency improvements",
                        "sources": ["google", "duckduckgo"],
                        "limit": 10
                    },
                    "expected_output": "20 deduplicated academic sources"
                }
            ]
        },
        
        "generate_report": {
            "description": "Generate comprehensive research reports from session data",
            "features": [
                "Multiple output formats (Markdown, HTML, JSON)",
                "Customizable report sections",
                "Professional citations and bibliography",
                "Executive summaries with key statistics",
                "Research methodology documentation"
            ],
            "parameters": {
                "session_id": "Research session ID from start_research (required)",
                "format": "markdown | html | json",
                "sections": "List of sections to include"
            },
            "available_sections": [
                "executive_summary",
                "key_findings", 
                "search_results",
                "sources",
                "methodology",
                "detailed_analysis",
                "limitations",
                "conclusion"
            ],
            "examples": [
                {
                    "name": "Full Research Report",
                    "request": {
                        "session_id": "research_1",
                        "format": "markdown",
                        "sections": ["executive_summary", "key_findings", "sources", "methodology", "conclusion"]
                    },
                    "expected_output": "Comprehensive Markdown report with all sections"
                },
                {
                    "name": "Quick Summary Report",
                    "request": {
                        "session_id": "research_2", 
                        "format": "html",
                        "sections": ["executive_summary", "key_findings"]
                    },
                    "expected_output": "Concise HTML summary report"
                }
            ]
        },
        
        "fact_check": {
            "description": "Fact-check statements against multiple sources",
            "features": [
                "Multi-source verification process",
                "Supporting and contradicting evidence analysis",
                "Confidence level assessment",
                "Source credibility evaluation",
                "Detailed evidence documentation"
            ],
            "parameters": {
                "statement": "Statement to fact-check (required)",
                "context": "Additional context for verification (optional)"
            },
            "examples": [
                {
                    "name": "Scientific Claim Verification",
                    "request": {
                        "statement": "COVID-19 vaccines have an efficacy rate of over 90%",
                        "context": "mRNA vaccines like Pfizer and Moderna"
                    },
                    "expected_output": "Detailed verification with supporting studies"
                },
                {
                    "name": "Technology Fact Check",
                    "request": {
                        "statement": "OpenAI GPT-4 has 1.76 trillion parameters",
                        "context": "Large language model specifications"
                    },
                    "expected_output": "Evidence-based assessment of parameter claims"
                },
                {
                    "name": "Environmental Data Check",
                    "request": {
                        "statement": "Global temperature has risen 1.1°C since pre-industrial times"
                    },
                    "expected_output": "Climate data verification from multiple sources"
                }
            ]
        }
    }
    
    for tool_name, tool_info in tools_examples.items():
        print(f"\n🔧 {tool_name.upper()}")
        print("=" * 50)
        print(f"**Description:** {tool_info['description']}\n")
        
        print("**Key Features:**")
        for feature in tool_info['features']:
            print(f"  • {feature}")
        print()
        
        print("**Parameters:**")
        for param, desc in tool_info['parameters'].items():
            print(f"  • **{param}**: {desc}")
        print()
        
        if 'available_sections' in tool_info:
            print("**Available Sections:**")
            for section in tool_info['available_sections']:
                print(f"  • {section}")
            print()
        
        print("**Usage Examples:**")
        for i, example in enumerate(tool_info['examples'], 1):
            print(f"\n  **{i}. {example['name']}**")
            print(f"  Request:")
            print(f"  ```json")
            print(f"  {json.dumps(example['request'], indent=2)}")
            print(f"  ```")
            print(f"  Expected: {example['expected_output']}")
        
        print("\n" + "=" * 50)

def demo_workflow_examples():
    """Demonstrate complete research workflows"""
    print("\n🎯 COMPLETE RESEARCH WORKFLOWS")
    print("=" * 60)
    
    workflows = [
        {
            "name": "Academic Research Workflow",
            "description": "Comprehensive research on scientific topics",
            "steps": [
                {
                    "step": 1,
                    "tool": "start_research",
                    "action": "Initialize comprehensive research",
                    "params": {
                        "topic": "CRISPR gene editing applications in medicine",
                        "depth": "comprehensive",
                        "sources": ["web", "news", "academic"]
                    }
                },
                {
                    "step": 2, 
                    "tool": "analyze_content",
                    "action": "Analyze key research papers",
                    "params": {
                        "url": "https://nature.com/articles/crispr-study",
                        "analysis_type": "key_points"
                    }
                },
                {
                    "step": 3,
                    "tool": "fact_check", 
                    "action": "Verify key claims",
                    "params": {
                        "statement": "CRISPR-Cas9 has 99% accuracy in targeted editing",
                        "context": "Gene editing precision studies"
                    }
                },
                {
                    "step": 4,
                    "tool": "generate_report",
                    "action": "Create comprehensive report",
                    "params": {
                        "session_id": "research_1",
                        "format": "markdown", 
                        "sections": ["executive_summary", "methodology", "key_findings", "sources", "limitations", "conclusion"]
                    }
                }
            ]
        },
        
        {
            "name": "Market Research Workflow",
            "description": "Business intelligence and market analysis",
            "steps": [
                {
                    "step": 1,
                    "tool": "start_research",
                    "action": "Start market research",
                    "params": {
                        "topic": "electric vehicle market trends 2024",
                        "depth": "deep",
                        "sources": ["web", "news"]
                    }
                },
                {
                    "step": 2,
                    "tool": "search_sources",
                    "action": "Find industry reports",
                    "params": {
                        "query": "EV sales statistics 2024 market share",
                        "sources": ["google", "bing"],
                        "limit": 20
                    }
                },
                {
                    "step": 3,
                    "tool": "analyze_content",
                    "action": "Extract market statistics",
                    "params": {
                        "url": "https://example.com/ev-market-report",
                        "analysis_type": "statistics"
                    }
                },
                {
                    "step": 4,
                    "tool": "generate_report",
                    "action": "Generate business report",
                    "params": {
                        "session_id": "research_2",
                        "format": "html",
                        "sections": ["executive_summary", "key_findings", "detailed_analysis", "conclusion"]
                    }
                }
            ]
        },
        
        {
            "name": "Fact-Checking Workflow",
            "description": "Verify claims and analyze information accuracy",
            "steps": [
                {
                    "step": 1,
                    "tool": "search_sources",
                    "action": "Gather sources on topic",
                    "params": {
                        "query": "renewable energy efficiency solar panels 2024",
                        "sources": ["google", "duckduckgo"],
                        "limit": 15
                    }
                },
                {
                    "step": 2,
                    "tool": "analyze_content",
                    "action": "Extract facts from sources",
                    "params": {
                        "url": "https://energy.gov/solar-efficiency-report",
                        "analysis_type": "facts"
                    }
                },
                {
                    "step": 3,
                    "tool": "fact_check",
                    "action": "Verify specific claims",
                    "params": {
                        "statement": "Solar panel efficiency has improved 25% in the last 5 years",
                        "context": "Photovoltaic technology improvements"
                    }
                },
                {
                    "step": 4,
                    "tool": "start_research",
                    "action": "Comprehensive verification research",
                    "params": {
                        "topic": "solar panel efficiency improvements verification",
                        "depth": "deep",
                        "sources": ["web", "academic"]
                    }
                }
            ]
        }
    ]
    
    for workflow in workflows:
        print(f"\n📋 **{workflow['name']}**")
        print(f"*{workflow['description']}*\n")
        
        for step_info in workflow['steps']:
            print(f"**Step {step_info['step']}: {step_info['action']}**")
            print(f"Tool: `{step_info['tool']}`")
            print("Parameters:")
            print("```json")
            print(json.dumps(step_info['params'], indent=2))
            print("```\n")
        
        print("-" * 50)

def demo_fastmcp_features():
    """Demonstrate FastMCP specific features"""
    print("\n⚡ FASTMCP SPECIFIC FEATURES")
    print("=" * 60)
    
    features = {
        "Type Safety with Pydantic": {
            "description": "Automatic request validation and type checking",
            "benefits": [
                "Prevents invalid parameters",
                "Clear parameter documentation",
                "IDE autocompletion support",
                "Runtime validation"
            ],
            "example": """
# Automatic validation ensures only valid depth values
ResearchRequest(
    topic="AI ethics",
    depth="invalid_depth"  # This would raise validation error
)
            """
        },
        
        "Context-Aware Logging": {
            "description": "Built-in logging and progress tracking",
            "benefits": [
                "Real-time progress updates",
                "Error tracking and debugging",
                "Performance monitoring",
                "User feedback"
            ],
            "example": """
ctx.info("Starting research...")
ctx.error("Failed to fetch URL")
ctx.debug("Processing 50 results")
            """
        },
        
        "Resource Management": {
            "description": "Structured access to server resources",
            "benefits": [
                "Session state persistence",
                "Report storage and retrieval",
                "Resource enumeration",
                "Data organization"
            ],
            "example": """
@mcp.resource("research://sessions")
def get_sessions():
    return current_research_sessions
            """
        },
        
        "Prompt Integration": {
            "description": "Built-in help and guidance system",
            "benefits": [
                "Interactive help system",
                "Usage examples",
                "Best practices guidance",
                "Workflow suggestions"
            ],
            "example": """
@mcp.prompt("research-help")
def research_help():
    return "Complete usage guide..."
            """
        }
    }
    
    for feature_name, feature_info in features.items():
        print(f"\n🔸 **{feature_name}**")
        print(f"{feature_info['description']}\n")
        
        print("**Benefits:**")
        for benefit in feature_info['benefits']:
            print(f"  • {benefit}")
        
        print(f"\n**Example:**")
        print(f"```python{feature_info['example']}```")
        print("\n" + "-" * 40)

def main():
    """Main demo function"""
    print("🚀 DEEP RESEARCH MCP SERVER - FASTMCP EDITION")
    print("=" * 70)
    print("Advanced web research and content analysis with modern FastMCP framework\n")
    
    sections = [
        ("FastMCP Tool Definitions", demo_fastmcp_tools),
        ("Complete Research Workflows", demo_workflow_examples), 
        ("FastMCP Framework Features", demo_fastmcp_features),
    ]
    
    print("Available demonstrations:")
    for i, (name, _) in enumerate(sections, 1):
        print(f"{i}. {name}")
    print("0. Run all demonstrations")
    
    try:
        choice = input("\nEnter choice (0-3): ").strip()
        
        if choice == "0":
            for name, func in sections:
                print(f"\n{'='*20} {name.upper()} {'='*20}")
                func()
        elif choice.isdigit() and 1 <= int(choice) <= len(sections):
            name, func = sections[int(choice) - 1]
            print(f"\n{'='*20} {name.upper()} {'='*20}")
            func()
        else:
            print("Invalid choice. Running all demonstrations by default.")
            for name, func in sections:
                print(f"\n{'='*20} {name.upper()} {'='*20}")
                func()
                
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError running demo: {e}")
    
    print(f"\n{'='*70}")
    print("🎯 Ready to use Deep Research MCP Server!")
    print("Run with: python main.py")
    print("Add to Claude Desktop MCP configuration to get started.")

if __name__ == "__main__":
    main()