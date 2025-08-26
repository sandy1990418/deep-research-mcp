#!/usr/bin/env python3
"""
Debug script to test the complete search workflow
"""

import asyncio
import os
import logging
from research_engine import ResearchEngine, ResearchConfig

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_chinese_search():
    """Debug the Chinese search issue"""
    print("🔍 Debugging Chinese Search Issue")
    print("=" * 60)
    
    engine = ResearchEngine()
    
    # Test queries in different languages
    test_queries = [
        ("人工智慧在醫療領域的應用", "Chinese"),
        ("artificial intelligence in healthcare", "English"),
        ("AI healthcare applications", "English simple")
    ]
    
    for query, lang in test_queries:
        print(f"\n🔸 Testing {lang} query: '{query}'")
        print("-" * 40)
        
        try:
            # Test Google Grounding first
            print(f"📍 Testing Google Grounding (API key: {engine.google_api_key[:10] if engine.google_api_key else 'None'}...)")
            if engine.google_api_key:
                grounding_results = await engine._search_google_grounding(query, 2)
                
                if grounding_results:
                    print(f"✅ Grounding: {len(grounding_results)} results")
                    for result in grounding_results:
                        print(f"   • {result.title[:60]}...")
                else:
                    print("⚠️  Grounding: No results")
            
            # Test fallback search
            print("🔄 Testing fallback search...")
            fallback_results = await engine._search_duckduckgo(query, 2)
            
            if fallback_results:
                print(f"✅ Fallback: {len(fallback_results)} results")
                for result in fallback_results:
                    print(f"   • {result.title[:60]}...")
            else:
                print("⚠️  Fallback: No results")
            
        except Exception as e:
            print(f"❌ Error for '{query}': {e}")
            logger.exception(f"Error testing query: {query}")
    
    print(f"\n{'=' * 60}")
    
    # Test full research workflow
    print("\n🎯 Testing Full Research Workflow")
    print("-" * 40)
    
    config = ResearchConfig(
        topic="人工智慧在醫療領域的應用",
        depth="basic",
        sources=["google"],
        language="zh"
    )
    
    try:
        print("Starting research workflow...")
        results = await engine.start_research(config)
        
        print(f"✅ Research completed!")
        print(f"   Total sources: {results.get('total_sources', 0)}")
        print(f"   Search results: {len(results.get('search_results', {}))}")
        print(f"   Key sources: {len(results.get('key_sources', []))}")
        print(f"   Key findings: {len(results.get('key_findings', []))}")
        
        # Show some details
        if results.get('search_results'):
            for source, source_results in results['search_results'].items():
                print(f"   {source}: {len(source_results)} results")
                if source_results:
                    print(f"      First result: {source_results[0].title[:50]}...")
        
    except Exception as e:
        print(f"❌ Research workflow error: {e}")
        logger.exception("Research workflow failed")

if __name__ == "__main__":
    asyncio.run(debug_chinese_search())