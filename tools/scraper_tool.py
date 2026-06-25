from crewai.tools import BaseTool
import urllib.request
import urllib.error
import os

class JinaReaderScraperTool(BaseTool):
    name: str = "Jina Reader Scraper Tool"
    description: str = "A tool to bypass complex DOM structures and extract clean markdown content from a given job URL using the Jina Reader API."
    
    def _run(self, url: str) -> str:
        # Jina Reader API URL
        jina_url = f"https://r.jina.ai/{url}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Accept": "text/event-stream" # Prefer markdown stream
        }
        
        req = urllib.request.Request(jina_url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8')
                return content if content else 'No markdown content extracted.'
        except urllib.error.URLError as e:
            return f"Failed to scrape URL {url} using Jina Reader. Error: {str(e)}"
        except Exception as e:
            return f"Unexpected error while scraping {url}: {str(e)}"
