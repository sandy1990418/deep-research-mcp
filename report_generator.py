"""
Report Generator - Generate comprehensive research reports
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate comprehensive research reports from research data"""
    
    def __init__(self):
        self.report_templates = {
            "markdown": self._generate_markdown_report,
            "html": self._generate_html_report,
            "json": self._generate_json_report,
        }
    
    async def generate_report(
        self, 
        session_data: Dict[str, Any], 
        format_type: str = "markdown",
        sections: List[str] = None
    ) -> str:
        """Generate a research report"""
        if sections is None:
            sections = ["executive_summary", "key_findings", "sources", "conclusion"]
        
        if format_type not in self.report_templates:
            format_type = "markdown"
        
        return await self.report_templates[format_type](session_data, sections)
    
    async def _generate_markdown_report(
        self, 
        session_data: Dict[str, Any], 
        sections: List[str]
    ) -> str:
        """Generate a Markdown research report"""
        try:
            topic = session_data.get('topic', 'Unknown Topic')
            config = session_data.get('config', {})
            results = session_data.get('results', {})
            
            # Start building the report
            report_parts = []
            
            # Header
            report_parts.append(f"# Deep Research Report: {topic}")
            report_parts.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*")
            report_parts.append("")
            
            # Research Configuration
            if 'config' in sections:
                report_parts.append("## Research Configuration")
                report_parts.append(f"- **Topic**: {topic}")
                report_parts.append(f"- **Depth**: {config.get('depth', 'Unknown')}")
                report_parts.append(f"- **Sources**: {', '.join(config.get('sources', []))}")
                report_parts.append(f"- **Language**: {config.get('language', 'en')}")
                report_parts.append("")
            
            # Executive Summary
            if 'executive_summary' in sections:
                summary = self._generate_executive_summary(session_data)
                report_parts.append("## Executive Summary")
                report_parts.append(summary)
                report_parts.append("")
            
            # Key Findings
            if 'key_findings' in sections:
                findings = self._format_key_findings(results.get('key_findings', []))
                report_parts.append("## Key Findings")
                report_parts.append(findings)
                report_parts.append("")
            
            # Search Results Summary
            if 'search_results' in sections:
                search_summary = self._format_search_results(results.get('search_results', {}))
                report_parts.append("## Search Results Summary")
                report_parts.append(search_summary)
                report_parts.append("")
            
            # Sources
            if 'sources' in sections:
                sources = self._format_sources(results.get('key_sources', []))
                report_parts.append("## Sources")
                report_parts.append(sources)
                report_parts.append("")
            
            # Methodology
            if 'methodology' in sections:
                methodology = self._generate_methodology_section(session_data)
                report_parts.append("## Research Methodology")
                report_parts.append(methodology)
                report_parts.append("")
            
            # Detailed Analysis
            if 'detailed_analysis' in sections:
                analysis = self._generate_detailed_analysis(results)
                report_parts.append("## Detailed Analysis")
                report_parts.append(analysis)
                report_parts.append("")
            
            # Limitations
            if 'limitations' in sections:
                limitations = self._generate_limitations_section(session_data)
                report_parts.append("## Research Limitations")
                report_parts.append(limitations)
                report_parts.append("")
            
            # Conclusion
            if 'conclusion' in sections:
                conclusion = self._generate_conclusion(session_data)
                report_parts.append("## Conclusion")
                report_parts.append(conclusion)
                report_parts.append("")
            
            # Footer
            report_parts.append("---")
            report_parts.append("*This report was generated using Deep Research MCP Server*")
            
            return "\n".join(report_parts)
            
        except Exception as e:
            logger.error(f"Markdown report generation failed: {e}")
            return f"Report generation failed: {str(e)}"
    
    def _generate_executive_summary(self, session_data: Dict[str, Any]) -> str:
        """Generate executive summary"""
        topic = session_data.get('topic', 'Unknown Topic')
        results = session_data.get('results', {})
        
        total_sources = results.get('total_sources', 0)
        key_findings_count = len(results.get('key_findings', []))
        
        summary = f"""This research report provides a comprehensive analysis of "{topic}". 
        
The investigation utilized {total_sources} sources across multiple search engines and databases, 
yielding {key_findings_count} key findings. The research employed both automated content analysis 
and structured information extraction to provide actionable insights.

**Key Statistics:**
- **Total Sources Analyzed**: {total_sources}
- **Key Findings Identified**: {key_findings_count}
- **Search Queries Used**: {len(results.get('queries_used', []))}
- **Primary Sources**: {len(results.get('key_sources', []))}"""

        return summary
    
    def _format_key_findings(self, findings: List[Dict[str, Any]]) -> str:
        """Format key findings section"""
        if not findings:
            return "No specific key findings were extracted from the analyzed sources."
        
        formatted_findings = []
        
        for i, finding in enumerate(findings, 1):
            title = finding.get('title', 'Unknown Source')
            source_url = finding.get('source', 'Unknown URL')
            key_points = finding.get('key_points', [])
            relevance = finding.get('relevance', 0.0)
            
            formatted_findings.append(f"### Finding #{i}: {title}")
            formatted_findings.append(f"**Source**: [{source_url}]({source_url})")
            formatted_findings.append(f"**Relevance Score**: {relevance:.2f}")
            formatted_findings.append("")
            
            if key_points:
                formatted_findings.append("**Key Points:**")
                for point in key_points:
                    formatted_findings.append(f"- {point}")
                formatted_findings.append("")
            else:
                formatted_findings.append("*No specific key points extracted*")
                formatted_findings.append("")
        
        return "\n".join(formatted_findings)
    
    def _format_search_results(self, search_results: Dict[str, List]) -> str:
        """Format search results summary"""
        if not search_results:
            return "No search results available."
        
        summary_parts = []
        
        for source, results in search_results.items():
            summary_parts.append(f"### {source.title()} Search Results")
            summary_parts.append(f"**Total Results**: {len(results)}")
            
            if results:
                summary_parts.append("**Top Results:**")
                for i, result in enumerate(results[:3], 1):
                    title = result.get('title', 'No title')
                    url = result.get('url', 'No URL')
                    snippet = result.get('snippet', 'No description')
                    
                    summary_parts.append(f"{i}. **[{title}]({url})**")
                    summary_parts.append(f"   {snippet}")
                    summary_parts.append("")
            else:
                summary_parts.append("*No results found*")
            
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def _format_sources(self, sources: List[Dict[str, Any]]) -> str:
        """Format sources section"""
        if not sources:
            return "No sources were analyzed."
        
        formatted_sources = []
        formatted_sources.append("### Primary Sources")
        formatted_sources.append("")
        
        for i, source in enumerate(sources, 1):
            if hasattr(source, 'title'):
                title = source.title
                url = source.url
                snippet = source.snippet
                relevance = source.relevance_score
            else:
                title = source.get('title', 'Unknown Title')
                url = source.get('url', 'Unknown URL')
                snippet = source.get('snippet', 'No description')
                relevance = source.get('relevance_score', 0.0)
            
            formatted_sources.append(f"{i}. **{title}**")
            formatted_sources.append(f"   - **URL**: {url}")
            formatted_sources.append(f"   - **Relevance**: {relevance:.2f}")
            formatted_sources.append(f"   - **Description**: {snippet}")
            formatted_sources.append("")
        
        # Add bibliography format
        formatted_sources.append("### Bibliography Format")
        formatted_sources.append("")
        
        for i, source in enumerate(sources, 1):
            if hasattr(source, 'title'):
                title = source.title
                url = source.url
            else:
                title = source.get('title', 'Unknown Title')
                url = source.get('url', 'Unknown URL')
            
            # Simple citation format
            formatted_sources.append(f"[{i}] \"{title}\" Retrieved from {url}")
        
        return "\n".join(formatted_sources)
    
    def _generate_methodology_section(self, session_data: Dict[str, Any]) -> str:
        """Generate methodology section"""
        config = session_data.get('config', {})
        results = session_data.get('results', {})
        
        methodology = f"""This research employed a multi-source web search and content analysis approach:

**Search Strategy:**
- **Primary Sources**: {', '.join(config.get('sources', []))}
- **Search Depth**: {config.get('depth', 'Unknown')} level analysis
- **Query Generation**: Automated query expansion based on topic keywords
- **Result Filtering**: Relevance-based ranking and deduplication

**Analysis Methods:**
- **Content Extraction**: Automated text extraction and cleaning
- **Key Point Identification**: Pattern-based information extraction
- **Source Verification**: Multi-source cross-referencing
- **Relevance Scoring**: Algorithm-based relevance assessment

**Quality Controls:**
- **Deduplication**: URL-based duplicate removal
- **Content Filtering**: Length and quality-based filtering  
- **Source Diversity**: Multi-engine search strategy
- **Rate Limiting**: Respectful crawling with delays"""

        return methodology
    
    def _generate_detailed_analysis(self, results: Dict[str, Any]) -> str:
        """Generate detailed analysis section"""
        findings = results.get('key_findings', [])
        
        if not findings:
            return "No detailed analysis available due to limited source data."
        
        analysis_parts = []
        
        # Analyze patterns across findings
        total_sources = len(findings)
        total_key_points = sum(len(f.get('key_points', [])) for f in findings)
        
        analysis_parts.append("### Cross-Source Analysis")
        analysis_parts.append(f"- **Sources Analyzed**: {total_sources}")
        analysis_parts.append(f"- **Key Points Extracted**: {total_key_points}")
        analysis_parts.append(f"- **Average Points per Source**: {total_key_points/max(total_sources, 1):.1f}")
        analysis_parts.append("")
        
        # Common themes analysis (simplified)
        all_text = " ".join([
            " ".join(f.get('key_points', []))
            for f in findings
        ]).lower()
        
        # Simple keyword frequency analysis
        common_words = self._extract_common_themes(all_text)
        
        if common_words:
            analysis_parts.append("### Common Themes Identified")
            for word, count in common_words:
                analysis_parts.append(f"- **{word.title()}**: Mentioned {count} times")
            analysis_parts.append("")
        
        # Source reliability analysis
        high_relevance_sources = [f for f in findings if f.get('relevance', 0) > 0.7]
        
        analysis_parts.append("### Source Quality Assessment")
        analysis_parts.append(f"- **High Relevance Sources**: {len(high_relevance_sources)} out of {total_sources}")
        analysis_parts.append(f"- **Average Relevance Score**: {sum(f.get('relevance', 0) for f in findings)/max(total_sources, 1):.2f}")
        analysis_parts.append("")
        
        return "\n".join(analysis_parts)
    
    def _extract_common_themes(self, text: str) -> List[tuple]:
        """Extract common themes from text (simplified approach)"""
        if not text:
            return []
        
        # Simple word frequency (excluding common words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        words = text.split()
        word_freq = {}
        
        for word in words:
            word = word.strip('.,!?;:"()[]').lower()
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top 5 most common words
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _generate_limitations_section(self, session_data: Dict[str, Any]) -> str:
        """Generate limitations section"""
        limitations = """This research has several inherent limitations:

**Technical Limitations:**
- **Search Scope**: Limited to publicly accessible web content
- **Language Bias**: Primarily focused on English-language sources
- **Temporal Scope**: Results reflect information available at time of search
- **Algorithm Dependency**: Relies on search engine algorithms for source discovery

**Content Analysis Limitations:**
- **Automated Processing**: Key point extraction is algorithm-based, not human-curated
- **Context Sensitivity**: May miss nuanced interpretations requiring domain expertise
- **Source Quality**: No manual verification of source credibility or accuracy
- **Completeness**: May not capture all relevant information on the topic

**Methodological Considerations:**
- **Sampling Bias**: Results dependent on search engine ranking algorithms
- **Recency Bias**: Newer content may be overrepresented
- **Accessibility**: Paywall and registration-protected content excluded
- **Dynamic Content**: JavaScript-heavy sites may not be fully analyzed"""

        return limitations
    
    def _generate_conclusion(self, session_data: Dict[str, Any]) -> str:
        """Generate conclusion section"""
        topic = session_data.get('topic', 'Unknown Topic')
        results = session_data.get('results', {})
        
        total_sources = results.get('total_sources', 0)
        key_findings_count = len(results.get('key_findings', []))
        
        if key_findings_count == 0:
            return f"""This research on "{topic}" was unable to extract significant findings from the available sources. 
This may indicate either limited available information on the topic or challenges in source accessibility. 
Future research might benefit from accessing specialized databases or expert interviews."""
        
        conclusion = f"""This comprehensive research on "{topic}" successfully analyzed {total_sources} sources and extracted {key_findings_count} key findings.

**Research Outcomes:**
- Successfully gathered information from multiple authoritative sources
- Identified key themes and patterns in the available literature
- Provided structured analysis suitable for further investigation
- Established a foundation for deeper domain-specific research

**Recommendations for Future Research:**
- Consider accessing academic databases for peer-reviewed sources
- Include expert interviews for qualitative insights
- Expand search to include specialized industry publications
- Conduct longitudinal analysis for trend identification

This automated research provides a solid foundation for understanding "{topic}" and can serve as a starting point for more focused investigation."""

        return conclusion
    
    async def _generate_html_report(
        self, 
        session_data: Dict[str, Any], 
        sections: List[str]
    ) -> str:
        """Generate an HTML research report"""
        # Convert markdown to HTML (simplified)
        markdown_report = await self._generate_markdown_report(session_data, sections)
        
        # Simple markdown to HTML conversion
        html_content = markdown_report.replace('\n', '<br>\n')
        html_content = html_content.replace('# ', '<h1>').replace('</h1><br>', '</h1>')
        html_content = html_content.replace('## ', '<h2>').replace('</h2><br>', '</h2>')
        html_content = html_content.replace('### ', '<h3>').replace('</h3><br>', '</h3>')
        html_content = html_content.replace('**', '<strong>').replace('</strong>', '</strong>')
        html_content = html_content.replace('*', '<em>').replace('</em>', '</em>')
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deep Research Report: {session_data.get('topic', 'Unknown Topic')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .summary {{ background: #ecf0f1; padding: 15px; border-radius: 5px; }}
        .source {{ margin-bottom: 15px; padding: 10px; border-left: 3px solid #3498db; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""
        return html_template
    
    async def _generate_json_report(
        self, 
        session_data: Dict[str, Any], 
        sections: List[str]
    ) -> str:
        """Generate a JSON research report"""
        report_data = {
            "metadata": {
                "topic": session_data.get('topic', 'Unknown Topic'),
                "generated_at": datetime.now().isoformat(),
                "session_id": session_data.get('session_id', 'unknown'),
                "sections_included": sections
            },
            "configuration": session_data.get('config', {}),
            "results": session_data.get('results', {}),
            "summary": {
                "total_sources": session_data.get('results', {}).get('total_sources', 0),
                "key_findings_count": len(session_data.get('results', {}).get('key_findings', [])),
                "queries_used": session_data.get('results', {}).get('queries_used', []),
            }
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)