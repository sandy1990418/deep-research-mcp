"""
Research Engine - Core research functionality
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
import os
from dataclasses import dataclass, asdict
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote
import time

logger = logging.getLogger(__name__)

@dataclass
class ResearchConfig:
    """Configuration for research sessions"""
    topic: str
    depth: str = "intermediate"
    sources: List[str] = None
    language: str = "en"
    max_results: int = 20
    
    def dict(self):
        return asdict(self)

@dataclass
class SearchResult:
    """Individual search result"""
    title: str
    url: str
    snippet: str
    source: str
    relevance_score: float = 0.0
    content: Optional[str] = None

class ResearchEngine:
    """Main research engine for deep research tasks using Google Grounding Search"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        
        # Google Grounding API configuration
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.grounding_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        
        # Fallback search engines
        self.search_engines = {
            "google_grounding": self._search_google_grounding,
            "google": self._search_google_fallback,
            "bing": self._search_bing,
            "duckduckgo": self._search_duckduckgo,
        }
    
    async def start_research(self, config: ResearchConfig) -> Dict[str, Any]:
        """Start a comprehensive research session"""
        logger.info(f"Starting research on: {config.topic}")
        
        # Generate research queries based on topic
        research_queries = self._generate_research_queries(config.topic, config.depth)
        
        # Search all configured sources
        search_results = {}
        for source in config.sources:
            if source in ["web", "google", "bing", "duckduckgo"]:
                source_results = []
                logger.info(f"Searching {source} with {len(research_queries)} queries")
                
                for query in research_queries[:3]:  # Use top 3 queries per source
                    try:
                        logger.info(f"Searching {source} for: {query}")
                        results = await self._search_source(query, source, config.max_results // max(len(research_queries), 1))
                        logger.info(f"Found {len(results)} results from {source} for query: {query}")
                        source_results.extend(results)
                    except Exception as e:
                        logger.error(f"Search failed for {source} with query '{query}': {e}")
                        # Add a fallback result even if search fails
                        source_results.append(SearchResult(
                            title=f"Search failed for: {query}",
                            url=f"https://www.google.com/search?q={quote(query)}",
                            snippet=f"Automated search for '{query}' encountered issues. Manual search may be required.",
                            source=f"{source}_error",
                            relevance_score=0.1
                        ))
                
                logger.info(f"Total results for {source}: {len(source_results)}")
                search_results[source] = source_results
        
        # Analyze and rank results
        key_sources = self._identify_key_sources(search_results)
        
        # Extract key information with better processing
        key_findings = await self._extract_key_findings(key_sources, config.topic)
        
        # Ensure we have meaningful findings even from grounding results
        if not key_findings and search_results:
            logger.info("Creating summary findings from search results")
            for source_name, results in search_results.items():
                for result in results[:3]:  # Top 3 per source
                    if result.snippet and len(result.snippet) > 50:
                        key_findings.append({
                            "source": result.url,
                            "title": result.title,
                            "key_points": [result.snippet],
                            "relevance": result.relevance_score
                        })
        
        return {
            "queries_used": research_queries,
            "search_results": search_results,
            "key_sources": key_sources,
            "key_findings": key_findings,
            "total_sources": sum(len(results) for results in search_results.values())
        }
    
    def _generate_research_queries(self, topic: str, depth: str) -> List[str]:
        """Generate research queries based on topic and depth"""
        base_query = topic
        
        if depth == "basic":
            queries = [
                f"{topic}",
                f"what is {topic}",
                f"{topic} overview"
            ]
        elif depth == "intermediate":
            queries = [
                f"{topic}",
                f"{topic} analysis",
                f"{topic} research",
                f"{topic} trends 2024 2025",
                f"{topic} latest developments"
            ]
        elif depth == "deep":
            queries = [
                f"{topic}",
                f"{topic} comprehensive analysis",
                f"{topic} academic research",
                f"{topic} case studies",
                f"{topic} expert opinions",
                f"{topic} methodology",
                f"{topic} best practices"
            ]
        else:  # comprehensive
            queries = [
                f"{topic}",
                f"{topic} comprehensive study",
                f"{topic} academic research papers",
                f"{topic} systematic review",
                f"{topic} meta analysis",
                f"{topic} industry report",
                f"{topic} expert interviews",
                f"{topic} statistical data",
                f"{topic} future trends predictions",
                f"{topic} comparative analysis"
            ]
        
        return queries
    
    async def _search_source(self, query: str, source: str, limit: int = 10) -> List[SearchResult]:
        """Search a specific source"""
        # Prioritize Google Grounding if available
        if source in ["web", "google"] and self.google_api_key:
            return await self._search_google_grounding(query, limit)
        elif source in ["web", "google"]:
            return await self._search_google_fallback(query, limit)
        elif source in self.search_engines:
            return await self.search_engines[source](query, limit)
        else:
            logger.warning(f"Unknown search source: {source}")
            return []
    
    async def _search_google_grounding(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search using Google Grounding API (Gemini with web grounding)"""
        try:
            if not self.google_api_key:
                logger.warning("Google API key not available, falling back to regular search")
                return await self._search_google_fallback(query, limit)
            
            # Construct Grounding request with web search (correct format for Gemini 2.0+)
            request_body = {
                "contents": [{
                    "parts": [{
                        "text": f"Search for comprehensive information about: {query}. Provide detailed findings with proper citations."
                    }]
                }],
                "tools": [{
                    "google_search": {}
                }],
                "generationConfig": {
                    "temperature": 1.0,  # Recommended for grounding
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Make API request
            try:
                response = await self.client.post(
                    f"{self.grounding_endpoint}?key={self.google_api_key}",
                    json=request_body,
                    headers=headers
                )
                
                if response.status_code != 200:
                    logger.error(f"Grounding API error: {response.status_code} - {response.text}")
                    logger.info("Falling back to regular search methods")
                    return await self._search_google_fallback(query, limit)
                    
            except Exception as api_error:
                logger.error(f"Grounding API request failed: {api_error}")
                logger.info("Falling back to regular search methods")
                return await self._search_google_fallback(query, limit)
            
            data = response.json()
            results = []
            
            # Extract search results from grounding citations (Gemini 2.0+ format)
            if 'candidates' in data and data['candidates']:
                candidate = data['candidates'][0]
                
                # Check for grounding metadata (new format)
                if 'groundingMetadata' in candidate:
                    grounding_meta = candidate['groundingMetadata']
                    
                    # Extract grounding chunks (sources)
                    if 'groundingChunks' in grounding_meta:
                        chunks = grounding_meta['groundingChunks']
                        for i, chunk in enumerate(chunks[:limit]):
                            if 'web' in chunk:
                                web_info = chunk['web']
                                title = web_info.get('title', 'No title')
                                url = web_info.get('uri', 'No URL')
                                
                                # Try to get snippet from grounding supports
                                snippet = "Content from Google Search"
                                if 'groundingSupports' in grounding_meta:
                                    supports = grounding_meta['groundingSupports']
                                    for support in supports:
                                        if support.get('groundingChunkIndices') and i in support['groundingChunkIndices']:
                                            if 'segment' in support:
                                                snippet = support['segment'].get('text', snippet)
                                            break
                                
                                results.append(SearchResult(
                                    title=title,
                                    url=url,
                                    snippet=snippet,
                                    source="google_grounding",
                                    relevance_score=1.0 - (i * 0.05)
                                ))
                    
                    # Extract web search results if available
                    if 'webSearchQueries' in grounding_meta:
                        queries_used = grounding_meta['webSearchQueries']
                        logger.info(f"Grounding used queries: {queries_used}")
                
                # Extract the main content with grounding information
                if 'content' in candidate:
                    content_parts = candidate['content'].get('parts', [])
                    main_text = ""
                    for part in content_parts:
                        if 'text' in part:
                            main_text += part['text']
                    
                    if main_text and not results:
                        # If no specific sources found, create one result with the grounded content
                        results.append(SearchResult(
                            title=f"Grounded research: {query}",
                            url="https://www.google.com/search?q=" + quote(query),
                            snippet=main_text[:500] + "..." if len(main_text) > 500 else main_text,
                            source="google_grounding",
                            relevance_score=1.0
                        ))
            
            logger.info(f"Found {len(results)} Google Grounding results for: {query}")
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Google Grounding search failed: {e}")
            logger.info("Falling back to regular search methods")
            return await self._search_google_fallback(query, limit)
    
    async def _search_google_fallback(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search Google (using a simple scraping approach)"""
        try:
            # Use Google search URL
            search_url = f"https://www.google.com/search?q={quote(query)}&num={limit}"
            
            response = await self.client.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Parse Google search results
            search_divs = soup.find_all('div', class_='g')
            
            for div in search_divs[:limit]:
                try:
                    # Get title and link
                    title_elem = div.find('h3')
                    link_elem = div.find('a')
                    snippet_elem = div.find('span', {'data-ved': True}) or div.find('div', class_='VwiC3b')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text().strip()
                        url = link_elem.get('href', '')
                        snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                        
                        # Clean URL (remove Google redirect)
                        if url.startswith('/url?q='):
                            url = url.split('/url?q=')[1].split('&')[0]
                        
                        if url and not url.startswith('http'):
                            continue
                        
                        results.append(SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source="google",
                            relevance_score=1.0 - (len(results) * 0.1)  # Simple relevance scoring
                        ))
                
                except Exception as e:
                    logger.debug(f"Error parsing search result: {e}")
                    continue
            
            logger.info(f"Found {len(results)} Google results for: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return []
    
    async def _search_bing(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search Bing"""
        try:
            search_url = f"https://www.bing.com/search?q={quote(query)}&count={limit}"
            
            response = await self.client.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Parse Bing search results
            search_results = soup.find_all('li', class_='b_algo')
            
            for result in search_results[:limit]:
                try:
                    title_elem = result.find('h2')
                    link_elem = title_elem.find('a') if title_elem else None
                    snippet_elem = result.find('p') or result.find('div', class_='b_caption')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text().strip()
                        url = link_elem.get('href', '')
                        snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                        
                        results.append(SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source="bing",
                            relevance_score=1.0 - (len(results) * 0.1)
                        ))
                
                except Exception as e:
                    logger.debug(f"Error parsing Bing result: {e}")
                    continue
            
            logger.info(f"Found {len(results)} Bing results for: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Bing search failed: {e}")
            return []
    
    async def _search_duckduckgo(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search DuckDuckGo with improved error handling"""
        try:
            # DuckDuckGo instant answer API
            search_url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"
            
            response = await self.client.get(search_url)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Process DuckDuckGo instant answer
            if data.get('AbstractText'):
                results.append(SearchResult(
                    title=f"DuckDuckGo Summary: {query}",
                    url=data.get('AbstractURL', ''),
                    snippet=data.get('AbstractText', ''),
                    source="duckduckgo",
                    relevance_score=1.0
                ))
            
            # Process related topics
            related_topics = data.get('RelatedTopics', [])
            
            for i, topic in enumerate(related_topics[:limit]):
                if isinstance(topic, dict) and 'Text' in topic:
                    title = topic.get('Text', '')[:100] + "..." if len(topic.get('Text', '')) > 100 else topic.get('Text', '')
                    url = topic.get('FirstURL', '')
                    snippet = topic.get('Text', '')
                    
                    if title and url:
                        results.append(SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source="duckduckgo",
                            relevance_score=0.9 - (i * 0.1)
                        ))
            
            # If no results, create a basic result with the query info
            if not results:
                results.append(SearchResult(
                    title=f"Search query: {query}",
                    url="https://duckduckgo.com/?q=" + quote(query),
                    snippet=f"Search for '{query}' - no instant results available, but search can be performed manually.",
                    source="duckduckgo",
                    relevance_score=0.5
                ))
            
            logger.info(f"Found {len(results)} DuckDuckGo results for: {query}")
            return results[:limit]
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            # Return a minimal result even if API fails
            return [SearchResult(
                title=f"Fallback search for: {query}",
                url="https://duckduckgo.com/?q=" + quote(query),
                snippet=f"Unable to retrieve search results automatically. Manual search recommended for: {query}",
                source="duckduckgo_fallback",
                relevance_score=0.3
            )]
    
    def _identify_key_sources(self, search_results: Dict[str, List[SearchResult]]) -> List[SearchResult]:
        """Identify the most relevant sources across all search results"""
        all_results = []
        
        # Combine all results
        for source, results in search_results.items():
            all_results.extend(results)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        # Sort by relevance score and return top results
        unique_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return unique_results[:15]  # Return top 15 sources
    
    async def _extract_key_findings(self, sources: List[SearchResult], topic: str) -> List[Dict[str, Any]]:
        """Extract key findings from top sources"""
        findings = []
        
        # Process top sources to extract content
        for i, source in enumerate(sources[:5]):  # Process top 5 sources
            try:
                content = await self._fetch_page_content(source.url)
                if content:
                    source.content = content
                    
                    # Extract key points (simplified)
                    key_points = self._extract_key_points(content, topic)
                    
                    findings.append({
                        "source": source.url,
                        "title": source.title,
                        "key_points": key_points,
                        "relevance": source.relevance_score
                    })
                
                # Add delay to be respectful to servers
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to extract findings from {source.url}: {e}")
                continue
        
        return findings
    
    async def _fetch_page_content(self, url: str) -> Optional[str]:
        """Fetch and clean page content"""
        try:
            response = await self.client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text content
            content = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit content length
            if len(content) > 5000:
                content = content[:5000] + "..."
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to fetch content from {url}: {e}")
            return None
    
    def _extract_key_points(self, content: str, topic: str) -> List[str]:
        """Extract key points from content (simplified approach)"""
        key_points = []
        
        # Split into sentences
        sentences = content.split('. ')
        
        # Find sentences containing topic keywords
        topic_words = topic.lower().split()
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if sentence contains topic keywords
            relevance_score = sum(1 for word in topic_words if word in sentence_lower)
            
            if relevance_score > 0 and len(sentence) > 50 and len(sentence) < 300:
                key_points.append(sentence.strip())
        
        # Return top key points
        return key_points[:5]
    
    async def search_multiple_sources(
        self, 
        query: str, 
        sources: List[str], 
        limit: int = 10
    ) -> Dict[str, List[SearchResult]]:
        """Search multiple sources simultaneously"""
        tasks = []
        
        for source in sources:
            if source in self.search_engines or source in ["web", "google"]:
                tasks.append(self._search_source(query, source, limit))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        search_results = {}
        for i, source in enumerate(sources):
            if i < len(results) and not isinstance(results[i], Exception):
                search_results[source] = results[i]
            else:
                search_results[source] = []
        
        return search_results
    
    async def fact_check(self, statement: str, context: str = "") -> Dict[str, Any]:
        """Fact-check a statement against multiple sources"""
        # Generate fact-checking queries
        fact_check_queries = [
            f"{statement}",
            f"{statement} fact check",
            f"{statement} true or false",
            f"{statement} verification",
        ]
        
        all_results = []
        
        # Search for information about the statement
        for query in fact_check_queries:
            try:
                google_results = await self._search_google(query, 5)
                all_results.extend(google_results)
                await asyncio.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.error(f"Fact-check search failed: {e}")
        
        # Analyze results for supporting/contradicting evidence
        supporting_evidence = []
        contradicting_evidence = []
        sources_checked = []
        
        for result in all_results[:10]:  # Check top 10 results
            try:
                content = await self._fetch_page_content(result.url)
                if content:
                    sources_checked.append(result.url)
                    
                    # Simple analysis (could be enhanced with NLP)
                    content_lower = content.lower()
                    statement_lower = statement.lower()
                    
                    # Look for supporting evidence
                    if any(word in content_lower for word in ["confirmed", "verified", "true", "correct"]):
                        supporting_evidence.append({
                            "source": result.url,
                            "title": result.title,
                            "evidence": result.snippet
                        })
                    
                    # Look for contradicting evidence
                    if any(word in content_lower for word in ["false", "incorrect", "debunked", "myth"]):
                        contradicting_evidence.append({
                            "source": result.url,
                            "title": result.title,
                            "evidence": result.snippet
                        })
                
                await asyncio.sleep(1)  # Be respectful to servers
                
            except Exception as e:
                logger.error(f"Failed to analyze {result.url}: {e}")
                continue
        
        # Determine confidence level
        support_count = len(supporting_evidence)
        contradict_count = len(contradicting_evidence)
        
        if support_count > contradict_count * 2:
            status = "Likely True"
            confidence = "High" if support_count >= 3 else "Medium"
        elif contradict_count > support_count * 2:
            status = "Likely False"
            confidence = "High" if contradict_count >= 3 else "Medium"
        else:
            status = "Uncertain"
            confidence = "Low"
        
        return {
            "status": status,
            "confidence": confidence,
            "supporting_evidence": supporting_evidence,
            "contradicting_evidence": contradicting_evidence,
            "sources": sources_checked,
            "total_sources_checked": len(sources_checked)
        }
    
    async def close(self):
        """Clean up resources"""
        await self.client.aclose()