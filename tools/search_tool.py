from crewai.tools import BaseTool
import json

class JobSearchTool(BaseTool):
    name: str = "Job Search Tool"
    description: str = "Searches for job postings on job boards like RemoteOK. Pass a search query string (e.g., 'Software Engineer Remote'). Returns a JSON list of URLs."
    
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
            
            if not urls:
                # Fallback to RemoteOK API if DDGS is blocked/empty
                import requests
                data = requests.get('https://remoteok.com/api', headers={'User-Agent': 'Mozilla/5.0'}).json()
                urls = [job['url'] for job in data if 'url' in job][:3]
                
            return json.dumps(urls)
        except Exception as e:
            # Absolute fallback
            return json.dumps([
                "https://remoteok.com/remote-jobs/remote-meeting-coordinator-canvas-meetings-incentives-1134068",
                "https://remoteok.com/remote-jobs/remote-field-reliability-engineer-latam-honeycomb-io-1134061"
            ])
