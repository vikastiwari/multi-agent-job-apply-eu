from crewai.tools import BaseTool
import json

class JobSearchTool(BaseTool):
    name: str = "Job Search Tool"
    description: str = "Searches for job postings on LinkedIn and EURES. Pass a search query string (e.g., 'site:linkedin.com/jobs \"Software Engineer\" \"Germany\"'). Returns a JSON list of URLs."
    
    def _run(self, query: str) -> str:
        try:
            from duckduckgo_search import DDGS
            results = DDGS().text(query, max_results=10)
            urls = []
            if results:
                for res in results:
                    url = res.get('href')
                    if url:
                        urls.append(url)
            return json.dumps(urls)
        except Exception as e:
            return json.dumps([])
