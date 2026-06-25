from crewai.tools import BaseTool
from firecrawl import FirecrawlApp
import os

class FirecrawlScraperTool(BaseTool):
    name: str = "Firecrawl Scraper Tool"
    description: str = "A tool to extract markdown content from a given job URL using Firecrawl API."
    
    def _run(self, url: str) -> str:
        api_key = os.environ.get("FIRECRAWL_API_KEY")
        if not api_key or api_key == "your_firecrawl_api_key_here":
            return "Error: Valid FIRECRAWL_API_KEY is not set in environment."
        
        try:
            app = FirecrawlApp(api_key=api_key)
            scrape_result = app.scrape(url, formats=['markdown'])
            return scrape_result.markdown if scrape_result.markdown else 'No markdown content extracted.'
        except Exception as e:
            return f"Failed to scrape URL {url}. Error: {str(e)}"
