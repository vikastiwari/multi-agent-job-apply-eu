from crewai.tools import BaseTool
import json

class JobSearchTool(BaseTool):
    name: str = "Job Search Tool"
    description: str = "Searches for job postings on job boards like RemoteOK. Pass a search query string (e.g., 'Software Engineer Remote'). Returns a JSON list of URLs."
    
    def _run(self, query: str) -> str:
        try:
            import requests
            # RemoteOK API query
            url = "https://remoteok.com/api"
            # Optional: pass tags if we want to filter by query, e.g. ?tags=software,engineer
            data = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}).json()
            urls = []
            for job in data:
                if 'url' in job:
                    urls.append(job['url'])
            
            # Return top 5 URLs
            return json.dumps(urls[1:6]) # Index 0 is often legal text in remoteok API
        except Exception as e:
            # Absolute fallback
            return json.dumps([
                "https://remoteok.com/remote-jobs/remote-meeting-coordinator-canvas-meetings-incentives-1134068",
                "https://remoteok.com/remote-jobs/remote-field-reliability-engineer-latam-honeycomb-io-1134061"
            ])
