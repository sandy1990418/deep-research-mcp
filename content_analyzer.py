"""
Content Analyzer - Advanced content analysis and extraction
"""

import logging
from typing import Dict, Any, List, Optional, Union
import re
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import asyncio

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """Advanced content analysis and extraction"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
    
    async def analyze_url(self, url: str, analysis_type: str = "summary") -> str:
        """Analyze content from a URL"""
        try:
            # Fetch page content
            response = await self.client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract content based on analysis type
            if analysis_type == "summary":
                return await self._generate_summary(soup, url)
            elif analysis_type == "key_points":
                return await self._extract_key_points(soup)
            elif analysis_type == "facts":
                return await self._extract_facts(soup)
            elif analysis_type == "quotes":
                return await self._extract_quotes(soup)
            elif analysis_type == "statistics":
                return await self._extract_statistics(soup)
            else:
                return await self._generate_summary(soup, url)
                
        except Exception as e:
            logger.error(f"Failed to analyze URL {url}: {e}")
            return f"Analysis failed: {str(e)}"
    
    async def _generate_summary(self, soup: BeautifulSoup, url: str) -> str:
        """Generate a comprehensive summary of the content"""
        try:
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'advertisement']):
                element.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title found"
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ""
            
            # Extract main content
            main_content = self._extract_main_content(soup)
            
            # Extract headings structure
            headings = self._extract_headings(soup)
            
            # Extract key paragraphs
            key_paragraphs = self._extract_key_paragraphs(soup)
            
            # Build summary
            summary = f"""# Content Summary for: {title_text}

**URL**: {url}

**Meta Description**: {description if description else "No description available"}

## Main Content Structure
{self._format_headings(headings)}

## Key Information
{self._format_key_paragraphs(key_paragraphs)}

## Full Content Summary
{main_content[:2000]}{'...' if len(main_content) > 2000 else ''}

**Content Length**: {len(main_content)} characters
**Headings Found**: {len(headings)}
**Key Sections**: {len(key_paragraphs)}
"""
            
            return summary
            
        except Exception as e:
            return f"Summary generation failed: {str(e)}"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page"""
        # Try different content selectors
        content_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.main-content',
            '.content',
            '.post-content',
            '.entry-content',
            'body'
        ]
        
        content = ""
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = elements[0].get_text(separator=' ', strip=True)
                break
        
        if not content:
            # Fallback: get all text from body
            body = soup.find('body')
            if body:
                content = body.get_text(separator=' ', strip=True)
        
        # Clean up text
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract heading structure"""
        headings = []
        
        for i in range(1, 7):  # h1 to h6
            for heading in soup.find_all(f'h{i}'):
                headings.append({
                    'level': i,
                    'text': heading.get_text().strip(),
                    'id': heading.get('id', ''),
                })
        
        return headings
    
    def _extract_key_paragraphs(self, soup: BeautifulSoup) -> List[str]:
        """Extract key paragraphs based on length and position"""
        paragraphs = soup.find_all('p')
        key_paragraphs = []
        
        for p in paragraphs:
            text = p.get_text().strip()
            # Select paragraphs with meaningful length
            if 100 <= len(text) <= 800:
                key_paragraphs.append(text)
        
        # Return top 5 key paragraphs
        return key_paragraphs[:5]
    
    def _format_headings(self, headings: List[Dict[str, Any]]) -> str:
        """Format headings for display"""
        if not headings:
            return "No headings found"
        
        formatted = []
        for heading in headings:
            indent = "  " * (heading['level'] - 1)
            formatted.append(f"{indent}- {heading['text']}")
        
        return "\n".join(formatted)
    
    def _format_key_paragraphs(self, paragraphs: List[str]) -> str:
        """Format key paragraphs for display"""
        if not paragraphs:
            return "No key paragraphs found"
        
        formatted = []
        for i, paragraph in enumerate(paragraphs, 1):
            formatted.append(f"**{i}.** {paragraph}\n")
        
        return "\n".join(formatted)
    
    async def _extract_key_points(self, soup: BeautifulSoup) -> str:
        """Extract key points from content"""
        try:
            # Look for lists
            lists = soup.find_all(['ul', 'ol'])
            key_points = []
            
            for lst in lists:
                items = lst.find_all('li')
                for item in items:
                    text = item.get_text().strip()
                    if 10 <= len(text) <= 300:  # Reasonable length
                        key_points.append(text)
            
            # Also extract from paragraphs with bullet points or numbers
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                # Look for patterns like "1.", "•", "-", etc.
                if re.match(r'^[\d\•\-\*]\s+', text) and len(text) <= 300:
                    key_points.append(text)
            
            # Remove duplicates and limit
            unique_points = list(dict.fromkeys(key_points))[:15]
            
            if unique_points:
                formatted_points = []
                for i, point in enumerate(unique_points, 1):
                    formatted_points.append(f"{i}. {point}")
                
                return "## Key Points Extracted:\n\n" + "\n\n".join(formatted_points)
            else:
                return "No specific key points found in list format."
                
        except Exception as e:
            return f"Key points extraction failed: {str(e)}"
    
    async def _extract_facts(self, soup: BeautifulSoup) -> str:
        """Extract factual information and data"""
        try:
            facts = []
            text = soup.get_text()
            
            # Look for patterns that indicate facts
            fact_patterns = [
                r'\d{4}\s*[-–]\s*\d{4}',  # Date ranges
                r'\d+%',  # Percentages
                r'\$[\d,]+(?:\.\d{2})?',  # Money amounts
                r'\d+(?:,\d{3})*(?:\.\d+)?',  # Numbers with commas
                r'(?:founded|established|created|launched|started)\s+in\s+\d{4}',  # Founding dates
                r'(?:approximately|about|around|over|under|more than|less than)\s+\d+(?:,\d{3})*',  # Approximate numbers
            ]
            
            sentences = re.split(r'[.!?]+', text)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if 20 <= len(sentence) <= 200:  # Reasonable sentence length
                    # Check if sentence contains factual patterns
                    for pattern in fact_patterns:
                        if re.search(pattern, sentence, re.IGNORECASE):
                            facts.append(sentence)
                            break
            
            # Remove duplicates and limit
            unique_facts = list(dict.fromkeys(facts))[:10]
            
            if unique_facts:
                formatted_facts = []
                for i, fact in enumerate(unique_facts, 1):
                    formatted_facts.append(f"{i}. {fact}")
                
                return "## Facts and Data Points:\n\n" + "\n\n".join(formatted_facts)
            else:
                return "No specific factual data patterns found."
                
        except Exception as e:
            return f"Facts extraction failed: {str(e)}"
    
    async def _extract_quotes(self, soup: BeautifulSoup) -> str:
        """Extract quotes and important statements"""
        try:
            quotes = []
            
            # Look for blockquotes
            blockquotes = soup.find_all('blockquote')
            for bq in blockquotes:
                quote_text = bq.get_text().strip()
                if 20 <= len(quote_text) <= 500:
                    quotes.append(quote_text)
            
            # Look for quoted text in paragraphs
            text = soup.get_text()
            quote_patterns = [
                r'"([^"]{20,300})"',  # Double quotes
                r'"([^"]{20,300})"',  # Smart quotes  
                r'\"([^\"]{20,300})\"',  # Escaped quotes
            ]
            
            for pattern in quote_patterns:
                matches = re.findall(pattern, text)
                quotes.extend(matches)
            
            # Remove duplicates and limit
            unique_quotes = list(dict.fromkeys(quotes))[:8]
            
            if unique_quotes:
                formatted_quotes = []
                for i, quote in enumerate(unique_quotes, 1):
                    formatted_quotes.append(f"{i}. \"{quote}\"")
                
                return "## Notable Quotes:\n\n" + "\n\n".join(formatted_quotes)
            else:
                return "No notable quotes found."
                
        except Exception as e:
            return f"Quotes extraction failed: {str(e)}"
    
    async def _extract_statistics(self, soup: BeautifulSoup) -> str:
        """Extract statistical information"""
        try:
            statistics = []
            text = soup.get_text()
            
            # Statistical patterns
            stat_patterns = [
                r'\d+(?:\.\d+)?%\s+(?:of|increase|decrease|growth|decline)',  # Percentages with context
                r'(?:increased|decreased|grew|fell|rose|dropped)\s+by\s+\d+(?:\.\d+)?%',  # Change percentages
                r'\d+(?:,\d{3})*\s+(?:people|users|customers|companies|participants)',  # Population numbers
                r'(?:revenue|profit|sales|income)\s+of\s+\$[\d,]+(?:\.\d+)?(?:\s+(?:million|billion|thousand))?',  # Financial figures
                r'\d+(?:\.\d+)?\s+(?:million|billion|thousand|hundred)\s+(?:people|users|dollars|pounds|euros)',  # Large numbers
                r'(?:average|median|mean)\s+(?:of\s+)?\$?[\d,]+(?:\.\d+)?',  # Averages
            ]
            
            sentences = re.split(r'[.!?]+', text)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if 15 <= len(sentence) <= 250:  # Reasonable sentence length
                    # Check if sentence contains statistical patterns
                    for pattern in stat_patterns:
                        if re.search(pattern, sentence, re.IGNORECASE):
                            statistics.append(sentence)
                            break
            
            # Also look for tables which often contain statistics
            tables = soup.find_all('table')
            for table in tables:
                table_text = table.get_text().strip()
                if 'statistic' in table_text.lower() or any(char.isdigit() for char in table_text):
                    # Extract table content (simplified)
                    rows = table.find_all('tr')
                    for row in rows[:3]:  # First 3 rows
                        row_text = row.get_text().strip()
                        if len(row_text) > 10 and any(char.isdigit() for char in row_text):
                            statistics.append(f"Table data: {row_text}")
            
            # Remove duplicates and limit
            unique_stats = list(dict.fromkeys(statistics))[:10]
            
            if unique_stats:
                formatted_stats = []
                for i, stat in enumerate(unique_stats, 1):
                    formatted_stats.append(f"{i}. {stat}")
                
                return "## Statistics and Data:\n\n" + "\n\n".join(formatted_stats)
            else:
                return "No statistical data found."
                
        except Exception as e:
            return f"Statistics extraction failed: {str(e)}"
    
    async def extract_structured_data(self, url: str) -> Dict[str, Any]:
        """Extract structured data from a webpage"""
        try:
            response = await self.client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract various structured data
            structured_data = {
                'url': url,
                'title': self._get_title(soup),
                'meta_description': self._get_meta_description(soup),
                'headings': self._extract_headings(soup),
                'links': self._extract_links(soup, url),
                'images': self._extract_images(soup, url),
                'content_length': len(soup.get_text()),
                'language': self._detect_language(soup),
                'last_modified': self._get_last_modified(soup),
                'author': self._get_author(soup),
                'publish_date': self._get_publish_date(soup),
            }
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Structured data extraction failed for {url}: {e}")
            return {'error': str(e)}
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title = soup.find('title')
        return title.get_text().strip() if title else ""
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta = soup.find('meta', attrs={'name': 'description'})
        return meta.get('content', '') if meta else ""
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links from page"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            
            # Convert relative URLs to absolute
            if href:
                full_url = urljoin(base_url, href)
                links.append({
                    'url': full_url,
                    'text': text,
                    'is_external': urlparse(full_url).netloc != urlparse(base_url).netloc
                })
        
        return links[:20]  # Limit to first 20 links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract images from page"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img.get('src')
            alt = img.get('alt', '')
            
            if src:
                full_url = urljoin(base_url, src)
                images.append({
                    'url': full_url,
                    'alt': alt
                })
        
        return images[:10]  # Limit to first 10 images
    
    def _detect_language(self, soup: BeautifulSoup) -> str:
        """Detect page language"""
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag.get('lang')
        
        # Try meta tag
        meta_lang = soup.find('meta', attrs={'http-equiv': 'content-language'})
        if meta_lang:
            return meta_lang.get('content', 'unknown')
        
        return 'unknown'
    
    def _get_last_modified(self, soup: BeautifulSoup) -> str:
        """Extract last modified date"""
        # Try various meta tags
        selectors = [
            'meta[name="last-modified"]',
            'meta[property="article:modified_time"]',
            'meta[name="date"]'
        ]
        
        for selector in selectors:
            meta = soup.select_one(selector)
            if meta:
                return meta.get('content', '')
        
        return ''
    
    def _get_author(self, soup: BeautifulSoup) -> str:
        """Extract author information"""
        # Try various meta tags and elements
        selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '.author',
            '.byline',
            '[rel="author"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content', '')
                else:
                    return element.get_text().strip()
        
        return ''
    
    def _get_publish_date(self, soup: BeautifulSoup) -> str:
        """Extract publish date"""
        selectors = [
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            'time[datetime]',
            '.publish-date',
            '.date'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content', '')
                elif element.name == 'time':
                    return element.get('datetime', '') or element.get_text().strip()
                else:
                    return element.get_text().strip()
        
        return ''
    
    async def close(self):
        """Clean up resources"""
        await self.client.aclose()